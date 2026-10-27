from src.model import train_model


if __name__ == "__main__":
    _, accuracy = train_model()
    print(f"Model trained. Accuracy: {accuracy:.3f}")
