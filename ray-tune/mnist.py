import os, json
from torchvision import datasets, transforms
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from filelock import FileLock
import ray
from ray import tune

DATA_ROOT  = '../data/mnist'
EPOCH_SIZE = 512
TEST_SIZE  = 256

# Code that was defined inline in the 02 lesson, but loaded from this file
# in subsequent lessons.

class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 3, kernel_size=3)
        self.fc = nn.Linear(192, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 3))
        x = x.view(-1, 192)
        x = self.fc(x)
        return F.log_softmax(x, dim=1)

def get_data_loaders():
    mnist_transforms = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.1307, ), (0.3081, ))])

    # We add FileLock here because multiple workers on the same machine coulde try
    # download the data. This would cause overwrites, since DataLoader is not threadsafe.
    # You wouldn't need this for single-process training.
    lock_file = f'{DATA_ROOT}/data.lock'
    import os
    if not os.path.exists(DATA_ROOT):
        os.makedirs(DATA_ROOT)

    with FileLock(os.path.expanduser(lock_file)):
        train_loader = torch.utils.data.DataLoader(
            datasets.MNIST(DATA_ROOT, train=True, download=True, transform=mnist_transforms),
            batch_size=64,
            shuffle=True)

        test_loader = torch.utils.data.DataLoader(
            datasets.MNIST(DATA_ROOT, train=False, transform=mnist_transforms),
            batch_size=64,
            shuffle=True)
    return train_loader, test_loader

# In the notebook, this was called "train" and it referenced EPOCH_SIZE directly.
# Here, we eliminate the global variable by returning a closure.
def make_train_step(bound):
    def train_step(model, optimizer, train_loader, device=torch.device("cpu")):
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            if batch_idx * len(data) > bound:
                return
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
    return train_step

# In the notebook, this was called "test" and it referenced TEST_SIZE directly.
# Here, we eliminate the global variable by returning a closure.
def make_test_step(bound):
    def test_step(model, data_loader, device=torch.device("cpu")):
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(data_loader):
                if batch_idx * len(data) > bound:
                    break
                data, target = data.to(device), target.to(device)
                outputs = model(data)
                _, predicted = torch.max(outputs.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        return correct / total
    return test_step

# This is called train_mnist in the notebook, but it's redefined later to be
# what we call train_mnist in this file:
def train_mnist_no_tune(config):
    train_loader, test_loader = get_data_loaders()
    model      = ConvNet()
    optimizer  = optim.SGD(model.parameters(), lr=config["lr"], momentum=config['momentum'])
    train_step = make_train_step(EPOCH_SIZE)
    test_step  = make_test_step(TEST_SIZE)
    for i in range(10):
        train_step(model, optimizer, train_loader)
        acc = test_step(model, test_loader)
        print(acc)

def train_mnist(config):
    from ray.tune import report
    train_loader, test_loader = get_data_loaders()
    model      = ConvNet()
    optimizer  = optim.SGD(model.parameters(), lr=config["lr"], momentum=config['momentum'])
    train_step = make_train_step(EPOCH_SIZE)
    test_step  = make_test_step(TEST_SIZE)
    for i in range(10):
        train_step(model, optimizer, train_loader)
        acc = test_step(model, test_loader)
        report(mean_accuracy=acc)

# This class implements more features than the notebook version,
# including the ability to save and restore from checkpoints and the
# tracking of timesteps, following this example:
# https://github.com/ray-project/ray/blob/releases/0.8.6/python/ray/tune/examples/bohb_example.py
class TrainMNIST(tune.Trainable):
    def _setup(self, config):
        self.timestep = 0
        self.config = config
        self.train_loader, self.test_loader = get_data_loaders()
        self.model = ConvNet()
        self.optimizer = optim.SGD(self.model.parameters(), lr=self.config["lr"])
        self.train_step = make_train_step(EPOCH_SIZE)
        self.test_step  = make_test_step(TEST_SIZE)

    def _train(self):
        self.timestep += 1
        self.train_step(self.model, self.optimizer, self.train_loader)
        acc = self.test_step(self.model, self.test_loader)
        return {"mean_accuracy": acc}


    def _save(self, checkpoint_dir):
        path = os.path.join(checkpoint_dir, "checkpoint")
        with open(path, "w") as f:
            f.write(json.dumps({"timestep": self.timestep}))
        return path

    def _restore(self, checkpoint_path):
        with open(checkpoint_path) as f:
            self.timestep = json.loads(f.read())["timestep"]


if __name__ == '__main__':

    config = {
        "lr": tune.grid_search([0.001, 0.01, 0.1]),
        "momentum": tune.grid_search([0.001, 0.01, 0.1, 0.9])
    }

    analysis = tune.run(
        TrainMNIST,
        config=config,
        stop={"training_iteration": 10},
        verbose=1,                                # Change to 0 or 1 to reduce the output.
        ray_auto_init=False                       # Don't allow Tune to initialize Ray.
    )
    print("Best config: ", analysis.get_best_config(metric="mean_accuracy"))
    print("Best performing trials:")
    print(analysis.dataframe().sort_values('mean_accuracy', ascending=False).head())