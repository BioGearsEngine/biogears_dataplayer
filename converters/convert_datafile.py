import os
import json
from math import floor

from lttb import largest_triangle_three_buckets

downsample_amounts = {
    'HeartRate(1/min)': 0.01,
    'HeartStrokeVolume(mL)': 0.03,
    'ExtravascularFluidVolume(L)': 0.02,
    'BloodVolume(mL)': 0.001,
    'ArterialPressure(mmHg)': 0.1,
    'MeanArterialPressure(mmHg)': 0.05,
    'SystolicArterialPressure(mmHg)': 0.03,
    'DiastolicArterialPressure(mmHg)': 0.03,
    'CardiacOutput(L/min)': 0.03,
    'HemoglobinContent(g)': 0.01,
    'CentralVenousPressure(mmHg)': 0.02,
    'PulmonaryCapillariesWedgePressure(mmHg)': 0.01,
    'RespirationRate(1/min)': 0.01,
    'OxygenSaturation': 0.01,
    'OxygenConsumptionRate(mL/min)': 0.01,
    'TidalVolume(mL)': 0.01,
    'TotalLungVolume(L)': 0.02,
    'EndTidalCarbonDioxideFraction': 0.01,
    'Aorta-Oxygen-PartialPressure(mmHg)': 0.15,
    'Aorta-CarbonDioxide-PartialPressure(mmHg)': 0.15,
    'Trachea-Oxygen-PartialPressure(cmH2O)': 0.02,
    'Trachea-CarbonDioxide-PartialPressure(cmH2O)': 0.02,
    'Lead3ElectricPotential(mV)': 0.5,
    'TotalMetabolicRate(kcal/day)': 0.01,
    'SkinTemperature(degC)': 0.01,
    'CoreTemperature(degC)': 0.01,
    'CarbonDioxideProductionRate(mL/min)': 0.01,
    'SweatRate(mg/min)': 0.01,
    'TotalWorkRateLevel': 0.01,
    'FatigueLevel': 0.01,
    'AchievedExerciseLevel': 0.01,
    'BloodPH': 0.01
    #'AirwayOxygenPartialPressure(cmH2O)': 0.01,
    #'AirwayCarbonDioxidePartialPressure(cmH2O)': 0.01,
    #'InspiredTidalVolume(mL)': 0.01,
    #'ExpiredTidalVolume(L)': 0.01
}


def downsample_amount(series):
    if series in downsample_amounts:
        return downsample_amounts[series]
    else:
        return 0.2


def parse_datafile(filepath):
    headers_map = []
    series = {}
    downsampled = {}
    headers_read = False

    with open(filepath) as f:
        for line in f:
            if headers_read:
                x = 0  # x is time
                for index, data in enumerate(list(map(str.strip, line.split(",")))):
                    if index is 0:
                        x = float(data)
                    else:
                        y = float(data)
                        series[headers_map[index-1]].append([x, y])  # We remove 1 to account for the time header
            else:
                for index, header in enumerate(list(map(str.strip, line.split(",")))):
                    if index > 0 and len(header) > 0:  # skip the time header
                        headers_map.append(header)
                        series[header] = []
                headers_read = True

    for header, data in series.items():
        amount = downsample_amount(header)
        print("Downsample amount for series " + header + ": " + str(amount))
        threshold = int(floor(amount * len(data)))
        print("Length of data: " + str(len(data)))
        print("LTTB threshold for series " + header + ": " + str(threshold))
        downsampled[header] = largest_triangle_three_buckets(data=data, threshold=threshold)
        print("Series " + header + " has been downsampled.")

    return downsampled


if __name__ == '__main__':
    for path, directories, filenames in os.walk("inputs"):
        for filename in filenames:
            if ".txt" in filename or ".csv" in filename:
                print("Parsing datafile: " + filename)

                contents = parse_datafile(os.path.join(path, filename))

                basename = os.path.splitext(os.path.basename(filename))[0]
                with open(os.path.join("outputs", basename + '-datafile.json'), 'w+') as f:
                    json.dump(contents, f, ensure_ascii=False)

                print("Datafile converted: " + basename + '-datafile.json')
