import numpy as np
import pandas as pd
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
		self.classify_energy_prices()

	def load_energy_prices(self, file_path: str) -> pd.DataFrame:
		"""Load electricity prices data from the provided file path."""
		try:
			return pd.read_csv(file_path)
		except Exception as e:
			print(f"Error loading energy prices file: {e}")
			return pd.DataFrame()

	def classify_energy_prices(self):
		"""Organize energy prices by station id ."""
		if not self.energy_prices.empty:
			grouped = self.energy_prices.groupby("station_id")  # classify the price data based on id
			self.station_prices = {station_id: data for station_id, data in grouped}
			# station id as key in the dictionary and data classified based on id as value

	def get_cost_estimated(self, station_id, possible_start_time, possible_end_time, power_consumption):

		if station_id not in self.station_prices:
			print(f"Station ID {station_id} not found in the prices data.")
			return float('inf')

		price_data = self.station_prices[station_id]
		predicted_charging_cost = 0.0

		for index, row in price_data.iterrows():
			# iterate each row in the price DataFrame and select the valid time interval
			overlap_start = max(row["range_start"], possible_start_time)
			# if the possible start time is later than start of one range, then it will be start of charging duration
			overlap_end = min(row["range_end"], possible_end_time)
			# if the possible end time earlier than the end of one range, then it will be end of charging duration

			if overlap_start < overlap_end:
				overlap_duration = overlap_end - overlap_start
				overlap_charging_amount = power_consumption * overlap_duration / 3600
				segment_charging_cost = overlap_charging_amount * row["price"]
				# calculate charging cost for each time segment with corresponding duration and price
				predicted_charging_cost += segment_charging_cost

		return predicted_charging_cost if predicted_charging_cost > 0 else float('inf')


