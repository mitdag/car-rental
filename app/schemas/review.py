from cgitb import text
from datetime import datetime
from pydantic import BaseModel

class Review_Base(BaseModel):
      review_id: int
      rental_id: int
      reviewer_id: int
      reviewee_id: int
      rating: int
      comment: text
      review_date: datetime
    
class Display_Review(BaseModel):
      review_id: int
      rental_id: int
      reviewer_id: int
      reviewee_id: int
      rating: int
      comment: text
      review_date: datetime



    
