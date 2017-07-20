import requests
import pandas
import folium
import json
from bs4 import BeautifulSoup

r = requests.get("http://www.pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/")
c = r.content

soup = BeautifulSoup(c,"html.parser")
all = soup.find_all("div",{"class":"propertyRow"})

page_nr = soup.find_all("a",{"class":"Page"})[-1].text

data_list = []
base_url = "http://www.pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/t=0&s="
for page in range(0,int(page_nr)*10,10):
    print(base_url + str(page) + ".html")
    r = requests.get(base_url + str(page) + ".html")
    c = r.content
    soup = BeautifulSoup(c,"html.parser")
    all = soup.find_all("div",{"class":"propertyRow"})
    for item in all:
        data_dict = {}
        data_dict["Price"] = item.find("h4",{"class":"propPrice"}).text.replace("\n","").replace(" ","")
        data_dict["Address"] = item.find_all("span",{"class":"propAddressCollapse"})[0].text
        try:
            data_dict["Locality"] = item.find_all("span",{"class":"propAddressCollapse"})[1].text
        except:
            data_dict["Locality"] = None
        try:
            data_dict["Beds"] = item.find("span",{"class":"infoBed"}).find("b").text
        except:
            data_dict["Beds"] = None
        try:
            data_dict["Area"] = item.find("span",{"class":"infoSqFt"}).find("b").text
        except:
            data_dict["Area"] = None
        try:
            data_dict["Full Baths"] = item.find("span",{"class":"infoValueFullBath"}).find("b").text
        except:
            data_dict["Full Baths"] = None
        try:
            data_dict["Half Baths"] = item.find("span",{"class":"infoValueHalfBath"}).find("b").text
        except:
            data_dict["Half Baths"] = None

        for col_group in item.find_all("div",{"class":"columnGroup"}):
            # print(col_group)
            for feature_Group,feature_Name in zip(col_group.find_all("span",{"class":"featureGroup"}), col_group.find_all("span",{"class":"featureName"})):
                # print(feature_Group.text, feature_Name.text)
                if "Lot Size" in feature_Group.text:
                    data_dict["Lot Size"] = feature_Name.text

        data_list.append(data_dict)

df = pandas.DataFrame(data_list)
df.to_csv("Data.csv")
# print(df)

# ---------------------------------------Map------------------------------------------------
def getLatlng(address = ""):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyB0BT3ka-gt1NYYwPgdtDEmUCLTrB6zvyE"
    r = requests.get(base_url)
    c = r.content
    d = json.loads(c)
    lat = d['results'][0]['geometry']['location']['lat']
    lng = d['results'][0]['geometry']['location']['lng']
    print(lat, lng)
    return lat, lng

tlat = []
tlng = []
tprice = []
tAddress = []
tLocality = []
for item in data_list:
    try:
        lat,lng = getLatlng(item['Address'])
        tlat.append(lat)
        tlng.append(lng)
        tprice.append(item['Price'])
        tAddress.append(item['Address'])
        tLocality.append(item['Locality'])
    except:
        pass


map = folium.Map(location=[38.58,-99.09], zoom_start=6, tiles="Mapbox Bright")

fgmarker = folium.FeatureGroup(name = "Marker Layer")

for lt, ln, pr, ad, lo in zip(tlat, tlng, tprice, tAddress, tLocality):
    fgmarker.add_child(folium.Marker(location=[lt, ln], popup = pr + '\n' + ad + '\n' + lo, icon = folium.Icon(color='blue')))

map.add_child(fgmarker)
map.add_child(folium.LayerControl())

map.save("Map1.html")

print("Finish~~~~~~~")