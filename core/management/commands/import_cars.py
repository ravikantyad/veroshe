from django.core.management.base import BaseCommand
import pandas as pd
from core.models import Car  # adjust as needed

class Command(BaseCommand):
    help = 'Import car data from Excel'

    def handle(self, *args, **kwargs):
        df = pd.read_excel("cleaned_car_data.xlsx")

        for _, row in df.iterrows():
            make = row['Make']
            model = row['Model']
            submodels = str(row['Submodel']).split(',')
            for submodel in submodels:
                Car.objects.create(
                    make=make.strip(),
                    model=model.strip(),
                    submodel=submodel.strip()
                )

        self.stdout.write(self.style.SUCCESS('Car data imported successfully.'))