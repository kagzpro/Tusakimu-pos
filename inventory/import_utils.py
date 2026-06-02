# inventory/import_utils.py
import csv
import io
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Product, Category, ProductUnit, ProductStock, Location

def get_user_locations(user):
    """Get locations accessible to the user"""
    locations = Location.objects.all()
    if locations.exists():
        return list(locations)
    return []

def process_product_import(request):
    """Process product import from CSV"""
    if request.method != 'POST':
        user_locations = get_user_locations(request.user)
        return render(request, 'inventory/import_products.html', {
            'user_locations': user_locations,
            'location_count': len(user_locations),
        })
    
    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        messages.error(request, "Please select a CSV file")
        return redirect('inventory:import_products')
    
    try:
        # Read the CSV file
        content = csv_file.read().decode('utf-8-sig')
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            messages.error(request, "CSV file is empty")
            return redirect('inventory:import_products')
        
        # Parse header
        header = lines[0].split(',')
        header = [h.strip().strip('"') for h in header]
        
        print(f"\n{'='*60}")
        print(f"CSV HEADER FOUND: {len(header)} columns")
        print(f"{'='*60}")
        for i, col in enumerate(header[:25]):
            print(f"  {i}: '{col}'")
        print(f"{'='*60}\n")
        
        # Create column mapping
        col_index = {col: idx for idx, col in enumerate(header)}
        
        # Verify required columns
        if 'Name' not in col_index or 'SKU' not in col_index:
            messages.error(request, "CSV must have 'Name' and 'SKU' columns")
            return redirect('inventory:import_products')
        
        # Get user locations
        user_locations = get_user_locations(request.user)
        print(f"User locations found: {[loc.name for loc in user_locations]}")
        
        # Statistics
        stats = {
            'created': 0,
            'updated': 0,
            'units': 0,
            'errors': []
        }
        
        # Process each row
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue
            
            # Parse row
            row = line.split(',')
            row = [r.strip() for r in row]
            
            # Get basic info
            name = row[col_index['Name']] if col_index['Name'] < len(row) else ''
            sku = row[col_index['SKU']] if col_index['SKU'] < len(row) else ''
            
            if not name or not sku:
                if name or sku:
                    stats['errors'].append(f"Row {line_num}: Missing name or SKU")
                continue
            
            print(f"\n--- Row {line_num}: {name} (SKU: {sku}) ---")
            
            # Get optional fields
            category = None
            if 'Category' in col_index and col_index['Category'] < len(row) and row[col_index['Category']]:
                cat_name = row[col_index['Category']]
                category, _ = Category.objects.get_or_create(name=cat_name)
                print(f"  Category: {cat_name}")
            
            base_unit = 'piece'
            if 'Base Unit' in col_index and col_index['Base Unit'] < len(row) and row[col_index['Base Unit']]:
                base_unit = row[col_index['Base Unit']]
            print(f"  Base Unit: {base_unit}")
            
            # Get prices
            try:
                cost_price = float(row[col_index['Cost Price']]) if 'Cost Price' in col_index and col_index['Cost Price'] < len(row) and row[col_index['Cost Price']] else 0
            except:
                cost_price = 0
            
            try:
                selling_price = float(row[col_index['Selling Price']]) if 'Selling Price' in col_index and col_index['Selling Price'] < len(row) and row[col_index['Selling Price']] else 0
            except:
                selling_price = 0
            
            print(f"  Prices: Cost={cost_price}, Selling={selling_price}")
            
            # Create or update product
            product, created = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': category,
                    'base_unit': base_unit,
                    'cost_price': cost_price,
                    'selling_price': selling_price,
                }
            )
            
            if created:
                stats['created'] += 1
                print(f"  ✓ Created NEW product")
            else:
                stats['updated'] += 1
                print(f"  ✓ Updated EXISTING product")
            
            # Process UNITS - NOW INCLUDING THE BASE UNIT
            units_found = 0
            
            # FIRST, ensure the base unit exists (piece, dozen, etc.)
            # This is the default selling unit
            base_unit_obj, base_created = ProductUnit.objects.update_or_create(
                product=product,
                unit_name=base_unit.lower(),
                defaults={
                    'quantity_in_base': 1.0,  # Base unit always has quantity 1 in itself
                    'selling_price': selling_price,  # Use the product's selling price
                    'is_default': True  # Mark as default unit
                }
            )
            stats['units'] += 1
            units_found += 1
            print(f"  ✓ DEFAULT UNIT: {base_unit} (quantity: 1, price: {selling_price})")
            
            # THEN process additional units from CSV (carton, box, packet, etc.)
            for unit_num in range(1, 6):  # Check for up to 5 units
                unit_name_col = f'Unit{unit_num}_Name'
                unit_qty_col = f'Unit{unit_num}_QtyInBase'
                unit_price_col = f'Unit{unit_num}_Price'
                
                if unit_name_col in col_index and unit_qty_col in col_index:
                    unit_name = row[col_index[unit_name_col]] if col_index[unit_name_col] < len(row) else ''
                    unit_qty = row[col_index[unit_qty_col]] if col_index[unit_qty_col] < len(row) else ''
                    unit_price = row[col_index[unit_price_col]] if unit_price_col in col_index and col_index[unit_price_col] < len(row) else ''
                    
                    if unit_name and unit_qty and unit_qty != '':
                        try:
                            qty = float(unit_qty)
                            price = float(unit_price) if unit_price and unit_price != '' else 0
                            
                            # Skip if it's the same as base unit (already added above)
                            if unit_name.lower() == base_unit.lower():
                                print(f"  ℹ Skipping duplicate {unit_name} (already added as default)")
                                continue
                            
                            # Create or update the additional unit (carton, box, etc.)
                            product_unit, unit_created = ProductUnit.objects.update_or_create(
                                product=product,
                                unit_name=unit_name.lower(),
                                defaults={
                                    'quantity_in_base': qty,
                                    'selling_price': price,
                                    'is_default': False
                                }
                            )
                            stats['units'] += 1
                            units_found += 1
                            print(f"  ✓ Unit {unit_num}: {unit_name} = {qty} {base_unit}(s) @ {price}")
                        except Exception as e:
                            stats['errors'].append(f"Row {line_num}: Unit '{unit_name}' error - {str(e)}")
                            print(f"  ✗ Error with unit {unit_name}: {e}")
            
            if units_found == 1:
                print(f"  ℹ Only base unit found, no additional units")
            
            # Process stock for locations
            for location in user_locations:
                stock_col = f'Stock_{location.name}'
                if stock_col in col_index and col_index[stock_col] < len(row) and row[col_index[stock_col]]:
                    try:
                        stock_qty = int(float(row[col_index[stock_col]]))
                        if stock_qty > 0:
                            stock, stock_created = ProductStock.objects.update_or_create(
                                product=product,
                                location=location,
                                defaults={'quantity': stock_qty}
                            )
                            print(f"  ✓ Stock for {location.name}: {stock_qty}")
                    except Exception as e:
                        print(f"  ✗ Stock error for {location.name}: {e}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"IMPORT SUMMARY:")
        print(f"  Created: {stats['created']}")
        print(f"  Updated: {stats['updated']}")
        print(f"  Units added: {stats['units']}")
        print(f"  Errors: {len(stats['errors'])}")
        if stats['errors']:
            print(f"  First few errors:")
            for err in stats['errors'][:3]:
                print(f"    - {err}")
        print(f"{'='*60}\n")
        
        # Show results
        messages.success(
            request,
            f"Import complete! Created: {stats['created']}, Updated: {stats['updated']}, Units: {stats['units']}"
        )
        
        if stats['errors']:
            for error in stats['errors'][:5]:
                messages.warning(request, error)
        
        return redirect('inventory:product_list')
        
    except Exception as e:
        messages.error(request, f"Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect('inventory:import_products')
