import pickle


def save(*args, name="save.pckl"):
    with open(name, "wb") as f:
        pickle.dump(args, f)


def load(name="save.pckl"):
    try:
        with open(name, "rb") as f:
            return pickle.load(f)
    except Exception:
        return (None,)
