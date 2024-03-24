import requests

class storesZIP:
    def __init__(self, zipcode):
        self.zip = zipcode
        self.closest_stores = self.find_closest_stores(self.zip)

        if isinstance(self.closest_stores, list):
            print("Closest stores:")
            for idx, store in enumerate(self.closest_stores, 1):
                print(f"{idx}. {store.get('Address')} - {store.get('City')}, {store.get('State')} {store.get('Zipcode')}, Phone: {store.get('Phone')}")
        else:
            print(self.closest_stores)
        pass
    def get_closest_stores(self):
        addresses = []
        phones = []
        for item in self.closest_stores:
            add = ""
            add+=item["Address"]+","+item["City"] + "," + item["State"] + "," + item["Zipcode"]
            phones.append(item["Phone"])
            addresses.append(add)

        return [addresses, phones]
    def find_closest_stores(self, zipcode, num_of_stores=5):
        url = "https://apimdev.wakefern.com/mockexample/V1/getStoreDetails"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": "4ae9400a1eda4f14b3e7227f24b74b44",
            "User-Agent": "PostmanRuntime/7.32.3"
        }
        params = {
            "zipcode": zipcode
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            stores = data  
            if stores:
                sorted_stores = sorted(stores, key=lambda x: x.get("distance", float('inf')))
                closest_stores = sorted_stores[:num_of_stores]
                return closest_stores
            else:
                return "No stores found for the given ZIP code."
        else:
            return "Error:", response.status_code

    