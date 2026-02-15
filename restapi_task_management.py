from pydantic import BaseModel
from uuid import UUID, uuid4
from enum import Enum
from fastapi import FastAPI, HTTPException
from typing import List, Optional

app=FastAPI()




class TaskStatus(str,Enum):
    pending="pending"
    completed="completed"


class TaskResponse(BaseModel):
    id:UUID
    title:str
    description:str
    status:TaskStatus


class TaskCreate(BaseModel):
    title:str
    description:str
    status:TaskStatus




tasks=[]
    
@app.post("/tasks",response_model=TaskResponse)

def create_task(task:TaskCreate):
    new_task={
        "id":uuid4(),
        "title":task.title,
        "description":task.description,
        "status":task.status      

    }
    tasks.append(new_task)
    return new_task



@app.get("/tasks/{task_id}",response_model=TaskResponse)

def gettask(task_id:UUID):
    for task in tasks:
        if task["id"]==task_id:
         return task
    raise HTTPException(status_code=404, detail="Task not found")
    

@app.put("/tasks/{task_id}",response_model=TaskResponse)

def updatetask(task_id:UUID,updated_task:TaskCreate):
    for task in tasks:
        if task["id"]==task_id:         
            task["title"]=updated_task.title
            task["description"]=updated_task.description
            task["status"]=updated_task.status
            return task 
    raise HTTPException(status_code=404, detail="Task not found")
        
@app.delete("/tasks/{task_id}")

def deletetask(task_id:UUID):
    for task in tasks:
        if task["id"]==task_id:
            tasks.remove(task)
            return("message:task removed succefffuully")
    raise HTTPException(status_code=404, detail="Task not deleted")


