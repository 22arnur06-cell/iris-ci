from src.model import load_data, train_model


def test_data_shape():
    X, y = load_data()
    assert X.shape == (150, 4)
    assert len(y) == 150


def test_model_accuracy():
    _, accuracy = train_model()
    assert accuracy > 0.85


def test_prediction_valid_class():
    model, _ = train_model()
    prediction = model.predict([[5.1, 3.5, 1.4, 0.2]])
    assert prediction[0] in (0, 1, 2)
