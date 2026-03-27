# Formula 1 Elo
This is just a small project that calculates the ELO rating of formula 1 drivers based on their race results. This is just for fun.

## Current functionality
Currently the functionality is as follows. In the main the season can be adjusted, this has to be done in the set as well as in the ratings call.
The calculation checks for any cached data, like active drivers, and elo_ratings_over_time as to save on API requests, as they are blocked relatively quickly.
After the calculation the requested seasons are plotted, with all drivers displayed that participated in these seasons.

## Future Work
- Optimize calculation
- Offer more visualization capabilities.
