import wilib 
mission = wilib.Mission('sedna', 'hydron', debug=False)
price_t0 = mission.get_price(relic_tier=wilib.RELIC_TIER0)
print(price_t0)
mission.save()