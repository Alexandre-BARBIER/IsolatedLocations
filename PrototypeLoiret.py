import numpy as np
import pandas as pd
import time
from math import *
from sklearn import neighbors
from pathlib import Path  

# Used to get isoline to check if location is no futher than time T of driving from point V
from herepy import (
    IsolineRoutingApi,
    IsolineRoutingTransportMode,
    IsolineRoutingMode,
)

isoline_routing_api = IsolineRoutingApi(api_key="")

import flexpolyline as fp
from polygon import is_inside_polygon

USE_HERE = False

# This function returns list of locations with incomplete data to remove from df dataframe
def remove_incomplete(df):
    to_remove = []
    for row in df.itertuples():
        index = row.Index
        lat = row.lat
        long = row.long
        if isnan(long) or isnan(lat):
            to_remove.append(index)
    return to_remove

def main():
    # Used to calculate performance
    start = time.time()
    
    # Here example done for Loiret (department 45 in France)
    # Parameters were hardcoded as this is a prototype
    department ="45"
    df = pd.read_csv("data/adresses-cadastre-" + department + ".csv",sep=";")
    # Departments directly bordering department 45
    frontiere = ["18","28","41","58","77","89","91"]

    # All properties in bordering department
    frames = []
    for numb in frontiere:
        frames.append(pd.read_csv("data/adresses-cadastre-" + numb + ".csv",sep=";"))
    frontdf = pd.concat(frames)

    # Eliminate locations with incomplete data
    df.drop(remove_incomplete(df),inplace =True)
    frontdf.drop(remove_incomplete(frontdf),inplace =True)

    # Convert data to numpy array as this will be more efficient for distance computing
    X = df[["lat","long"]].to_numpy()
    Y = frontdf[["lat","long"]].to_numpy()

    # Number of elements in department
    indepart = X.shape[0]
    Z = np.concatenate((X,Y))

    # Latitude and longitude are in degrees but our distance computing algorithm uses angles in rads
    Z = (pi*Z)/180

    # Builds a structure efficient to identify nearest neighbors
    kdtree = neighbors.BallTree(Z, metric="haversine")
    # We ask for the 2 nearest neighbors as the first one will always be the point itself
    # We only query for first indepart points, are the other ones are in bordering departments, and thus out of scope
    dist, ind = kdtree.query(Z[:indepart],k=2)
    dist = dist*6371 #We multiply by Earth radius to get distance in kilometers, as this is an angular distance

    if USE_HERE:
        # Here the point V around which we are searching and sitance T are hardcoded as this is a prototype
        response = isoline_routing_api.time_isoline(
            transport_mode=IsolineRoutingTransportMode.car,
            origin=[48.857084238970735, 2.352139805155152], #V
            ranges=[7200], #T in seconds
        )
        dict = response.as_dict()

        polyline = dict['isolines'][0]['polygons'][0]['outer']
        routes = fp.decode(polyline)

    num = []
    Z = (Z*180)/pi
    for i in range(dist.shape[0]):
        if dist[i][1] >= 0.3:
            if df.iloc[i]['destination_principale'] == "habitation":
                if USE_HERE:
                    if (is_inside_polygon(points = routes, p = X[i])):
                        num.append(i)
                else:
                    num.append(i)

    newdf = df.iloc[num]
    filepath = Path('out.csv')
    newdf.to_csv(filepath,sep=";")
    end = time.time()
    print(end-start)

if __name__ == "__main__":
    main()
