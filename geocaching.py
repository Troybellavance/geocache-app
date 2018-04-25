from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim
import pandas
import datetime

 """A simple webapp that allows a user to submit a .csv file and obtain the geospatial
 coordinates of the addresses within."""

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

 
@app.route("/success", methods=['POST'])
def success():
    global csvfile
    #Function checks if the user submitted the correct type of file and turns it into a
    #pandas dataframe before geocoding and saving as a trimmed, time-stamped file for the user.
    if request.method=='POST':
        csvfile=request.files["csvfile"]
        try:
            df = pandas.read_csv(csvfile)
        except:
            return render_template("index.html", text="Please select a CSV file.")

        df = geocode(df)

        try:
            df = df[['address', 'Coordinates', 'Latitude', 'Longitude']]
            df.set_index('address')
        except KeyError:
            df = df[['Address', 'Coordinates', 'Latitude', 'Longitude']]
            df.set_index('Address')
        except Exception as e:
            return render_template("index.html", text="Please check that addresses are in an Address or address column in your file.")

        csvfile = datetime.datetime.now().strftime("uploads/%Y-%m-%d-%H-%M-%S"+".csv")
        df.to_csv(csvfile, index=None)
        return render_template("index.html", text=df.to_html(), btn="download.html", btn1 = "webmap.html", webmap="webmap.html")

       
@app.route("/download")
def download():
    return send_file(csvfile, attachment_filename="yourfile.csv", as_attachment=True)


def geocode(df):
    #Function checks dataframe generated and geocodes coordinates, logitutde and latitude from the address column.
    columns = [item.lower() for item in df.columns]
    nom=Nominatim(scheme="http")
    if "address" not in columns:
        return render_template("index.html", text="Please check that addresses are in an Address or address column in your file.")
    else:
        try:
            df['Coordinates'] = df["Address"].apply(nom.geocode)
        except Exception as address:
            df['Coordinates'] = df["address"].apply(nom.geocode)
        df['Longitude'] = df["Coordinates"].apply(lambda x: x.longitude if x is not None else None)
        df['Latitude'] = df["Coordinates"].apply(lambda x: x.latitude if x is not None else None)
        return df


if __name__ == "__main__":
    app.debug=False
    app.run()
