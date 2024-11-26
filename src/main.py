import datetime
import pickle

import numpy as np

from src.layers.activation_function import ActivationFunction
from src.layers.activation_layer import ActivationLayer
from src.layers.fully_connected_layer import FCLayer
from src.add_ons.learning_rate_schedulers import LearningRateScheduler
from src.add_ons.loss_function import LossFunction
from src.network import Network
from src.add_ons.optimizers import Optimizer
from src.utils.read_data import read_data, to_categorical
from src.config import EPOCHS, BATCH_SIZE, LOG_FILE


def main():
    # Create log file if it does not exist already
    try:
        with open(LOG_FILE, 'x') as log_file:
            pass
    except:
        pass

    # Read training and test data
    (x_train, y_train, x_test, y_test) = read_data()

    # reshape and normalize input data
    x_train = x_train.reshape(x_train.shape[0], 1, 28 * 28)
    x_train = x_train.astype('float32')
    x_train /= 255
    # Convert labels into one-hot encoding
    y_train = to_categorical(y_train)

    x_test = x_test.reshape(x_test.shape[0], 1, 28 * 28)
    x_test = x_test.astype('float32')
    x_test /= 255

    y_test = to_categorical(y_test)

    # Change model_to_load to filename in models/ to load a model. Otherwise a new model will be trained.
    model_to_load = None
    model = None

    if model_to_load is None:
        # If there is no model to load, create a new neural network
        model = create_model()

        # Train only on part of the data since all of it would be pretty slow since batches are not implemented yet
        model.set_loss_function(LossFunction.categorical_cross_entropy)
        model.fit(x_train, y_train, epochs=EPOCHS, learning_rate_scheduler=LearningRateScheduler.const, batch_size=BATCH_SIZE)

        # Save the model
        model_path = f"models/model_{datetime.datetime.now().strftime('%Y_%m_%dT%H:%M:%S')}.pkl"
        with open(model_path, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(model, f)
    else:
        model_path = f"models/{model_to_load}"
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    test_model(model, x_test, y_test)


def create_model() -> Network:
    model = Network()
    model.add_layer(FCLayer(28 * 28, 128, optimizer=Optimizer.Adam))  # input_shape=(1, 28*28)    ;   output_shape=(1, 100)
    model.add_layer(ActivationLayer(ActivationFunction.tanh, 128))
    # model.add_layer(FCLayer(100, 50))  # input_shape=(1, 100)      ;   output_shape=(1, 50)
    # model.add_layer(ActivationLayer(ActivationFunction.tanh, 50))
    model.add_layer(FCLayer(128, 10, optimizer=Optimizer.Adam))  # input_shape=(1, 50)       ;   output_shape=(1, 10)
    model.add_layer(ActivationLayer(ActivationFunction.softmax, 10))
    return model


def test_model(model: Network, x_test, y_test):
    predictions = model.predict(x_test)
    predictions_flattened = np.array(predictions).reshape(len(predictions), 10)

    # Convert predictions to label indices
    predicted_labels = np.argmax(predictions_flattened, axis=1)
    actual_labels = np.argmax(y_test, axis=1)

    # Compare predicted labels with true labels
    correct_predictions = np.sum(predicted_labels == actual_labels)

    # Log the results
    string_to_be_logged = f"Number of correctly recognized images: {correct_predictions} out of {len(x_test)}"
    print(string_to_be_logged)
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(string_to_be_logged + "\n")
    error = (len(x_test) - correct_predictions) / len(x_test)
    string_to_be_logged = f"The error rate is {error * 100}%"
    print(string_to_be_logged)
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(string_to_be_logged + "\n")


if __name__ == "__main__":
    main()
