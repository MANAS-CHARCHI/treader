import os
import django
import pandas as pd
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treader.settings")
django.setup()

from markets.models import Stocks

ASSETS_DIR = "markets/assets"


def import_bse_stocks():
    bse_file = os.path.join(ASSETS_DIR, "BSE_stocks.csv")
    df = pd.read_csv(bse_file)

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        isin = str(row['ISIN']).strip()
        company_name = str(row['Company_Name']).strip()
        bse_symbol = str(row['BSE_Scrip_Code']).strip()
        nse_symbol = str(row['NSE_Symbol']).strip() if not pd.isna(row['NSE_Symbol']) else None

        # Try to insert/update; skip if duplicate ISIN
        try:
            Stocks.objects.update_or_create(
                isin_number=isin,
                defaults={
                    "company_name": company_name,
                    "bse_symbol": bse_symbol,
                    "nse_symbol": nse_symbol,
                }
            )
            inserted += 1
        except Exception as e:
            skipped += 1
            print(f"Skipped duplicate or error for ISIN {isin}: {e}")

    print(f"Imported {inserted} BSE stocks, skipped {skipped} duplicates/errors.")


def import_nse_stocks():
    nse_file = os.path.join(ASSETS_DIR, "NSE_stocks.csv")
    df = pd.read_csv(nse_file)

    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        isin = str(row['ISIN']).strip()
        nse_symbol = str(row['SYMBOL']).strip()
        name_of_company = str(row['NAME_OF_COMPANY']).strip()

        # Update only if stock exists; ignore if duplicate ISIN
        try:
            stock = Stocks.objects.get(isin_number=isin)
            stock.nse_symbol = nse_symbol
            stock.company_name = name_of_company
            stock.save()
            updated += 1
        except Stocks.DoesNotExist:
            skipped += 1
            continue
        except Exception as e:
            skipped += 1
            print(f"Skipped duplicate or error for ISIN {isin}: {e}")

    print(f"Updated NSE symbols for {updated} stocks, skipped {skipped} not found/errors.")


if __name__ == "__main__":
    import_bse_stocks()
    import_nse_stocks()
    print("Stocks import completed.")
