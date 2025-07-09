from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DataBaseEnums import DataBaseEnum
# or  from bson.objectid import ObjectId
from bson import ObjectId



class AssetModel(BaseDataModel) :
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    
    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance



    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections :
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes :
                await self.collection.create_index(
                    index["key"],
                    name= index["name"],
                    unique= index["unique"]
                )



    async def create_asset(self, asset: Asset):
        # transform the pydantic schem to dictionary :
        result = await self.collection.insert_one(asset.dict(by_alias=True , exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    


    async def get_all_project_assets(self, asset_project_id: Asset , asset_type: str):
        
        records =  await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id ,
            "asset_type" : asset_type ,
        }).to_list(length=None)

        # turn the records to pydantic models :
        return [
            Asset(**record)
            for record in records
        ]
    

    




