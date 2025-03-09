import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
from pathlib import Path
import glob

def visualize_domain(file_path, save_path=None, show=True):
    """
    Visualize a domain file containing initial conditions with appropriate colormap.

    Args:
        file_path: Path to the domain.npy file
        save_path: Optional path to save the visualization
        show: Whether to display the plot
    """
    # Load the numpy array
    data = np.load(file_path)
    building_id = os.path.basename(file_path).split('_')[0]

    # Create figure
    plt.figure(figsize=(10, 8))

    # Plot the data with a colormap suitable for temperature
    im = plt.imshow(data, cmap='hot', interpolation='nearest')

    # Add a colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Temperature Value')

    # Add title and labels
    plt.title(f'Building {building_id}: Initial Temperature Conditions')
    plt.xlabel('X Grid Position')
    plt.ylabel('Y Grid Position')

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()

def visualize_interior(file_path, save_path=None, show=True):
    """
    Visualize an interior mask file with binary colormap.

    Args:
        file_path: Path to the interior.npy file
        save_path: Optional path to save the visualization
        show: Whether to display the plot
    """
    # Load the numpy array
    data = np.load(file_path)
    building_id = os.path.basename(file_path).split('_')[0]

    # Create figure
    plt.figure(figsize=(10, 8))

    # Plot the binary mask data
    im = plt.imshow(data, cmap='binary', interpolation='nearest')

    # Add a colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Mask Value (1=Interior, 0=Exterior/Walls)')

    # Add title and labels
    plt.title(f'Building {building_id}: Interior Mask')
    plt.xlabel('X Grid Position')
    plt.ylabel('Y Grid Position')

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()

def visualize_combined(domain_path, interior_path, save_path=None, show=True):
    """
    Create a combined visualization showing both temperature and interior mask.

    Args:
        domain_path: Path to the domain.npy file
        interior_path: Path to the interior.npy file
        save_path: Optional path to save the visualization
        show: Whether to display the plot
    """
    # Load the numpy arrays
    domain_data = np.load(domain_path)
    interior_data = np.load(interior_path)
    building_id = os.path.basename(domain_path).split('_')[0]

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Plot domain data (temperature)
    im1 = ax1.imshow(domain_data, cmap='hot', interpolation='nearest')
    ax1.set_title('Temperature Initial Conditions')
    ax1.set_xlabel('X Grid Position')
    ax1.set_ylabel('Y Grid Position')
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Temperature Value')

    # Plot interior mask
    im2 = ax2.imshow(interior_data, cmap='binary', interpolation='nearest')
    ax2.set_title('Interior Mask (1=Interior, 0=Exterior/Walls)')
    ax2.set_xlabel('X Grid Position')
    ax2.set_ylabel('Y Grid Position')
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.set_label('Mask Value')

    # Add overall title
    plt.suptitle(f'Building {building_id}: Heat Equation Simulation Data', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()

def process_directory(directory_path, output_dir=None, combined=True):
    """
    Process all .npy files in a directory, creating visualizations.

    Args:
        directory_path: Path to directory containing the .npy files
        output_dir: Directory to save output images (created if doesn't exist)
        combined: Whether to create combined visualizations
    """
    # Create output directory if specified and doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Find all domain and interior files
    domain_files = glob.glob(os.path.join(directory_path, "*_domain.npy"))

    for domain_file in domain_files:
        # Construct the expected interior file name
        base_name = os.path.basename(domain_file).split('_domain.npy')[0]
        interior_file = os.path.join(directory_path, f"{base_name}_interior.npy")

        # Check if both files exist
        if os.path.exists(interior_file):
            print(f"Processing building {base_name}...")

            # Define save paths if output directory is specified
            if output_dir:
                domain_save = os.path.join(output_dir, f"{base_name}_domain.png")
                interior_save = os.path.join(output_dir, f"{base_name}_interior.png")
                combined_save = os.path.join(output_dir, f"{base_name}_combined.png")
            else:
                domain_save = interior_save = combined_save = None

            # Create individual visualizations
            visualize_domain(domain_file, domain_save, show=False)
            visualize_interior(interior_file, interior_save, show=False)

            # Create combined visualization if requested
            if combined:
                visualize_combined(domain_file, interior_file, combined_save, show=False)

            print(f"  Visualizations for building {base_name} complete.")
        else:
            print(f"Warning: Could not find matching interior file for {domain_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize heat equation simulation data.')
    parser.add_argument('--dir', type=str, default='/dtu/projects/02613_2025/data/modified_swiss_dwellings/',
                        help='Directory containing the .npy files')
    parser.add_argument('--output', type=str, default='./visualization_output',
                        help='Directory to save output images')
    parser.add_argument('--building', type=str, default=None,
                        help='Specific building ID to process (optional)')
    parser.add_argument('--show', action='store_true',
                        help='Show plots interactively (default: save to files only)')
    parser.add_argument('--no-combined', dest='combined', action='store_false',
                        help='Skip combined visualizations')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    if args.building:
        # Process a specific building
        domain_file = os.path.join(args.dir, f"{args.building}_domain.npy")
        interior_file = os.path.join(args.dir, f"{args.building}_interior.npy")

        if os.path.exists(domain_file) and os.path.exists(interior_file):
            domain_save = os.path.join(args.output, f"{args.building}_domain.png")
            interior_save = os.path.join(args.output, f"{args.building}_interior.png")
            combined_save = os.path.join(args.output, f"{args.building}_combined.png")

            visualize_domain(domain_file, domain_save, show=args.show)
            visualize_interior(interior_file, interior_save, show=args.show)

            if args.combined:
                visualize_combined(domain_file, interior_file, combined_save, show=args.show)

            print(f"Visualizations for building {args.building} complete.")
        else:
            print(f"Error: Could not find files for building {args.building}")
    else:
        # Process all buildings in the directory
        process_directory(args.dir, args.output, combined=args.combined)
        print(f"All visualizations saved to {args.output}")
