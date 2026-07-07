import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile
from typing import List, Dict, Any
import asyncio
from core.cloudinary import cloudinary

class CloudinaryService:
    def __init__(self):
        self.folder = "event_images"
    
    async def upload_image(
        self, 
        file: UploadFile, 
        event_id: str,
        photographer_id: str,
        public_id: str = None
    ) -> Dict[str, Any]:
        """Upload single image to Cloudinary"""
        try:
            contents = await file.read()
            
            upload_options = {
                "folder": f"{self.folder}/photographer_{photographer_id}/event_{event_id}",
                "resource_type": "image",
                "use_filename": True,
                "unique_filename": True
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            result = cloudinary.uploader.upload(contents, **upload_options)
            
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("url"),
                "secure_url": result.get("secure_url"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "original_filename": result.get("original_filename")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def upload_multiple_images(
        self, 
        files: List[UploadFile], 
        event_id: str,
        photographer_id: str
    ) -> List[Dict[str, Any]]:
        """Upload multiple images in parallel"""
        tasks = []
        for file in files:
            await file.seek(0)
            tasks.append(self.upload_image(file, event_id, photographer_id))
        
        return await asyncio.gather(*tasks)
    
    async def delete_image(self, public_id: str) -> bool:
        """Delete image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="image")
            return result.get("result") == "ok"
        except Exception:
            return False
    
    async def delete_multiple_images(self, public_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple images"""
        tasks = [self.delete_image(pid) for pid in public_ids]
        results = await asyncio.gather(*tasks)
        
        return {pid: result for pid, result in zip(public_ids, results)}
    
def get_transformed_url(self, public_id: str, transformations: Dict[str, Any]) -> str:
    return cloudinary.CloudinaryImage(public_id).build_url(**transformations)