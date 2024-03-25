import plotly.graph_objects as go
import torch
import torch.nn as nn
import torch.optim as optim

import fetch


def show_stations_with_the_most_history(count=5, province="MANITOBA"):
    columns_to_print = [
        "Climate ID",
        "Station Name",
        "HLY_Interval",
        "DLY_Interval",
    ]
    sl = fetch.station_list()
    sl.loc[:, "HLY_Interval"] = sl.loc[:, "HLY Last Year"] - sl.loc[:, "HLY First Year"]
    sl.loc[:, "DLY_Interval"] = sl.loc[:, "DLY Last Year"] - sl.loc[:, "DLY First Year"]
    sl = sl[sl.Province == province]
    print("These stations have the most hourly data: ")
    print()
    print(
        sl.sort_values("HLY_Interval", ascending=False)[0:count][
            columns_to_print + ["HLY Last Year"]
        ]
    )
    print("These stations have the most daily data: ")
    print(
        sl.sort_values("DLY_Interval", ascending=False)[0:count][
            columns_to_print + ["DLY Last Year"]
        ]
    )
    print()


class WeatherPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(WeatherPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


my_climate_ids = {
    "Gretna": "5021220",
    "Pilot Mound": "5022125",
}
temperature_threshold = -10  # [C]

if __name__ == "__main__":
    print("Starting")
    show_stations_with_the_most_history()
    print("Getting all weather data...")
    station_to_use = "Gretna"
    hourly = fetch.all_hourly_for(my_climate_ids[station_to_use])
    print()
    print(
        f"Percent of hourly observations that have data: "
        f"{hourly.loc[:, 'Temp (°C)'].count()/len(hourly.index)*100:0.1f}%"
    )
    print()
    print("drawing figures...")
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=hourly["Date/Time (LST)"], y=hourly["Temp (°C)"], mode="markers", name="Min Temp"
        )
    )
    fig.update_layout(title=f"Daily Min Temperature at {station_to_use}")
    fig.show(renderer="browser")

    # Prepare the dataset
    x_train = hourly.loc[:, "Temp (°C)"][-101:-1].values
    y_train = hourly.loc[:, "Temp (°C)"].shift(-1)[-101:-1].values
    # convert to PyTorch tensors
    inputs = torch.tensor(x_train, dtype=torch.float32)
    targets = torch.tensor(y_train, dtype=torch.float32)

    # Define model parameters
    input_size = 1  # Number of features
    hidden_size = 64  # Number of neurons in the hidden layer
    output_size = 1  # Single output (weather prediction)

    # Instantiate the model, loss function, and optimizer
    model = WeatherPredictor(input_size, hidden_size, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    num_epochs = 100
    for epoch in range(num_epochs):

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

    # Now you can use the trained model for prediction
    # For example, if you have new observations, you can predict the weather for the next hour
    new_data = ...  # Your new observations
    with torch.no_grad():
        model.eval()
        prediction = model(torch.tensor(new_data, dtype=torch.float32))
        print("Predicted weather for the next hour:", prediction.item())
