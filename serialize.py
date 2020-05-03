import pickle


def save(*args, name="save.pckl"):
    with open(name, "wb") as f:
        pickle.dump(args, f)


def load(name="save.pckl"):
    with open(name, "rb") as f:
        return tuple(pickle.load(f))
