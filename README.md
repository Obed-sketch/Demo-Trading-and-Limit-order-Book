# Demo-Trading-and-Limit-order-Book

`Demo Trading Message Data and Limit Order Book.ipynb` — an executed
analysis notebook (41 cells, all outputs saved, no errors) that works with
limit-order-book message data: reconstructing and examining the order book
from exchange message traffic.

## Data requirement (not included)

The notebook reads two course data files that are **not in this repo**:

- `classdata/message.csv` — exchange message traffic
- `classdata/orderbook.csv` — order-book snapshots

These are licensed course datasets and are not redistributable, so the
notebook cannot be re-run from a fresh clone; it is presented as executed
work with its outputs intact. To re-run it, place the two CSVs in a
`classdata/` folder next to the notebook and execute top to bottom. Data in
the standard LOBSTER sample format (message/orderbook CSVs) is the closest
public equivalent.

## Dependencies

```bash
pip install -r requirements.txt
```
