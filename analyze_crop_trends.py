import os
import pandas as pd
import glob

# Get all crop folders
base_path = r"c:\Users\2022n\Desktop\llml\KisaanPragati"
crop_folders = [f for f in os.listdir(base_path) 
                if os.path.isdir(os.path.join(base_path, f)) and f != '__pycache__']

# List to store results
crop_avg_values = []

print("Analyzing crop trends from Year.csv files...\n")
print("=" * 60)

# Process each crop folder
for crop_folder in crop_folders:
    year_file = os.path.join(base_path, crop_folder, "Year.csv")
    
    # Check if Year.csv exists
    if os.path.exists(year_file):
        try:
            # Read the CSV file, skip first 2 rows (Category header)
            df = pd.read_csv(year_file, skiprows=2)
            
            # Get the value column (second column)
            value_column = df.columns[1]
            
            # Calculate average of all values (which represent the peak/trend values)
            avg_value = df[value_column].mean()
            
            # Store the result
            crop_avg_values.append({
                'Crop': crop_folder,
                'Average_Peak_Value': round(avg_value, 2)
            })
            
            print(f"✓ {crop_folder:20} - Average Peak Value: {avg_value:.2f}")
            
        except Exception as e:
            print(f"✗ {crop_folder:20} - Error: {str(e)}")
    else:
        print(f"✗ {crop_folder:20} - Year.csv not found")

# Create a DataFrame from results
result_df = pd.DataFrame(crop_avg_values)

# Sort by average value (descending)
result_df = result_df.sort_values('Average_Peak_Value', ascending=False)

# Save to CSV
output_file = os.path.join(base_path, "crop_average_peak_values.csv")
result_df.to_csv(output_file, index=False)

print("\n" + "=" * 60)
print(f"\nTotal crops analyzed: {len(crop_avg_values)}")
print(f"\nResults saved to: {output_file}")
print("\n" + "=" * 60)
print("\nTop 10 Crops by Average Peak Value:")
print(result_df.head(10).to_string(index=False))
print("\n" + "=" * 60)
print("\nFull List of Crops and Average Peak Values:")
print(result_df.to_string(index=False))
