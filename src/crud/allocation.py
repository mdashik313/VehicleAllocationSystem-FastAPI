from src.database import allocation_history, allocationDB_helper
from bson.objectid import ObjectId
from datetime import date, datetime
from motor.motor_asyncio import AsyncIOMotorCollection


#crud operations

# Retrieve allocation history
async def retrieve_allocations():
    allocations = []   
    async for allocation in allocation_history.find():    #query to fetch all allocation document and append each doucment in a list.
        allocations.append(allocationDB_helper(allocation))
    return allocations

# Create a new allocation to the database
async def add_allocation(allocation_data: dict) -> dict:   
    allocation = await allocation_history.insert_one(allocation_data)
    new_allocation = await allocation_history.find_one({"_id": allocation.inserted_id})
    return allocationDB_helper(new_allocation)


#Delete an allocation
async def delete_allocation_data(id : str):
    allocation = await allocation_history.find_one({"_id": ObjectId(id)})
    
    if allocation:
        allocation_date_str = datetime.strptime(allocation["allocation_date"], "%Y-%m-%d").date()
        if allocation_date_str <= date.today():
            return 0  # let 0 means date it is not future date
        else: 
            await allocation_history.delete_one({"_id": ObjectId(id)})
            return 1  # let 1 means successfully deleted
    return 2  #let 2 means date doesn't exist



#Update allocation
async def update_allocation_data(allocation_data: dict) -> tuple:
    
    # Check if the vehicle is already allocated for the given date
    existing_allocation = await allocation_history.find_one({
        "vehicle_id": allocation_data["vehicle_id"],
        "allocation_date": allocation_data["allocation_date"]
    })

    if existing_allocation:
        return allocation_data, "Vehicle is already allocated for this date."

    updated_allocation = await allocation_history.update_one(
        {"_id": ObjectId(allocation_data["allocation_id"])}, {"$set": {
            "vehicle_id" : allocation_data["vehicle_id"],
            "allocation_date" : allocation_data["allocation_date"]
        }}
    )

    if updated_allocation.modified_count:
        return allocation_data, "Allocation updated successfully."
    else:
        return allocation_data, "Allocation ID not found."
        

# Search allocations
async def filter_allocation(search_params: dict) -> list:

    # Check if allocation_id is provided
    if search_params.get("allocation_id"):
        if ObjectId.is_valid(search_params.get("allocation_id")):
            results = await allocation_history.find_one({"_id": ObjectId(search_params["allocation_id"])})
            if results:
                return allocationDB_helper(results)
            else:
                return [] 
        
    results = allocation_history.find({
        "$and": [
         search_params
    ]})
    
    allocation_list = []
    # Iterating over the result to retrieve documents
    async for allocation in results:
        allocation_list.append(allocationDB_helper(allocation))

    return allocation_list    