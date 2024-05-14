import numpy as np
import pandas as pd
from pandas import DataFrame
from src.misc.globals import *
from typing import Dict


class CostManager:
	"""Calculate the predicted cost for each station based on time."""
	def __init__(self, scenario_parameters: dict):
		self.scenario_parameters: dict = scenario_parameters
		self.cost_manager = None

		dir_names = get_directory_dict(self.scenario_parameters)
		energy_file_name = self.scenario_parameters.get(G_ENERGY_TIME_SERIES_FILE)
		energy_file_path = os.path.join(dir_names[G_DIR_INFRA], energy_file_name)
		self.energy_prices = pd.read_csv(energy_file_path)
		self.station_prices: Dict[int, pd.DataFrame] = {}
		self.process_energy_prices()

	def load_energy_prices(self, file_path: str) -> pd.DataFrame:
		"""Load electricity prices data from the provided file path."""
		try:
			return pd.read_csv(file_path)
		except Exception as e:
			print(f"Error loading energy prices file: {e}")
			return pd.DataFrame()

	def process_energy_prices(self):
		"""Organize energy prices by station id ."""
		if not self.energy_prices.empty:
			grouped = self.energy_prices.groupby("station_id")  # classify the price data based on id
			self.station_prices = {station_id: data for station_id, data in grouped}
			# station id as key in the dictionary and based on id classified data as value

	def get_cost_estimated(self, station_id, possible_start_time, possible_end_time, power_consumption):

		if station_id not in self.station_prices:
			print(f"Station ID {station_id} not found in the prices data.")
			return 0.0
		price_data = self.station_prices[station_id]
		charging_duration = possible_end_time - possible_start_time
		charging_amount = power_consumption * charging_duration / 3600

		price_data_in_time = price_data[
			(price_data["end_time"] > possible_start_time) &
			(price_data["start_time"] < possible_end_time)
			]
		# select the corresponding interval of prices based on possible start and end time.
		# make sure that possible start time of charging task is before the valid end time of price range.
		# & possible end time of charging task is after the valid start time of price range.

		if not price_data_in_time.empty:
			current_price = price_data_in_time['price'].mean()  # new selection algorithm, should not be one price only, multiple prices across different intervals should be included
		# if the charging time interval across two price ranges, then calculate with average price of 2 prices.
		# 需要选择多个价格然后，如果还是原来的逻辑，那么就是价格*到那个价格对应的时间点所充入的电量。

		else:
			return float('inf')

		predicted_charging_cost = charging_amount * current_price

		return predicted_charging_cost
