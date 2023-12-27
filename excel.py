import pandas as pd

# create a DataFrame from the given list
data = [
    [17750, 37650, 1256050, -3150, -107150, 3050, -74800, 0, 0],
    [17800, 250550, 4305400, 12550, -637200, 7250, -574200, 0, 0],
    [17850, 52000, 1160500, -200, -275850, -1850, -250200, 0, 0],
    [17900, 144000, 2810550, -104000, -1107800, -109300, -1054100, 0, 0],
    [17950, 69750, 1080800, -96750, -843000, -100300, -727600, 0, 0],
    [18000, 904000, 4321450, -558400, -2876850, -589050, -2869750, 0, 0],
    [18050, 420750, 960250, -189800, -1081850, -233750, -1028900, 0, 0],
    [18100, 2222950, 3603400, -1023200, -3245550, -1247950, -3027700, 0, 0],
    [18150, 1152750, 1182000, -1453050, -2382200, -1688550, -2266850, 0, 0],
    [18200, 7967050, 4411550, -1730250, -1662550, -1880100, -1221900, 0, 0],
    [18250, 3086150, 774250, -825900, -398750, -833850, -329250, 0, 0],
    [18300, 6628650, 1080850, -1021600, -432100, -1320150, -359850, 0, 0],
    [18350, 2001250, 283650, -383050, -48400, -410300, -33650, 0, 0],
    [18400, 5009200, 393000, -742850, -80200, -786000, -72850, 0, 0],
    [18450, 2144550, 129450, -733150, -28400, -630450, -24550, 0, 0],
    [18500, 6181400, 316750, -658650, 11050, -601000, 18100, 0, 0]
]

df = pd.DataFrame(data)

# save the DataFrame to an Excel file
df.to_excel('output.xlsx', index=False, header=False)