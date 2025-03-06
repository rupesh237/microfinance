import json
from django.core.management.base import BaseCommand

from dashboard.models import Province, District, Municipality

class Command(BaseCommand):
    help = 'import json data to database'

    def handle(self, *args, **kwargs):
        with open('province.json', 'r') as f:
            province_data = json.load(f)
            for province in province_data:
                # create provinces & re-fetch from DB
                Province.objects.create(
                    id=province['id'],
                    name=province['name']
                )
            # provinces = Province.objects.all()
            # print(provinces)

        with open('districts.json', 'r') as f:
            district_data = json.load(f)
            for district in district_data:
                # create districts & re-fetch from DB
                District.objects.create(
                    id=district['id'],
                    province_id=district['province_id'],
                    name=district['name']
                )
            # districts = District.objects.all()
            # print(districts)

        with open('municipality.json', 'r') as f:
            municipality_data = json.load(f)
            for municipality in municipality_data:
                # create municipalities & re-fetch from DB
                Municipality.objects.create(
                    id=municipality['id'],
                    district_id=municipality['district_id'],
                    name=municipality['name']
                )
            # municipalities = Municipality.objects.all()
            # print(municipalities)