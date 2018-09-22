import wiAPI as wiapi
from pprint import pprint
mission = wiapi.Mission('void', 'mithra')
mission.load_rewards(wiapi.MISSION_ROTATION_A)
mission.load_reward_total_sell_price()
print(mission.load_reward_total_sell_price)
