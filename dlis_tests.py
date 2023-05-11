# # Define the log parameters and data
# log_params = ['DEPT', 'DT', 'GR']
# log_data = [(1000.0, 100.0, 50.0),
#             (1001.0, 101.0, 51.0),
#             (1002.0, 102.0, 52.0)]
#
# # Define the header for each record
# record_header = '1OPEN/CLOSE LOG FILE'
# param_header = '3LOG PARAMETER DEFINITION'
#
# # Write the DLIS file
# with open('data.dlis', 'wb') as f:
#     # Write the record header
#     f.write(record_header.encode('utf-8'))
#
#     # Write the parameter header
#     f.write(param_header.encode('utf-8'))
#     for param in log_params:
#         f.write(f'4{param}'.encode('utf-8'))
#
#     # Write the log data
#     for data in log_data:
#         for value in data:
#             f.write(f'{value:.2f} '.encode('utf-8'))
#         f.write(b'\n')

# import welly


# Load the DLIS file
# with welly.DLISFile(r"C:\Users\kamil.grunwald\Desktop\data.dlis") as dlis:
import welly

# Load the DLIS file
lis = welly.LIS.from_file(r"C:\Users\kamil.grunwald\Desktop\data.dlis")

# Iterate over the curves in the DLIS file
for curve in lis.curves:
    # Print the curve header
    print(curve.header)

    # Convert the curve data to a pandas dataframe
    df = curve.df()
    print(df.head())