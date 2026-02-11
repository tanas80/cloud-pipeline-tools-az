from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class AutoUser(BaseModel):
    """Auto user account settings"""
    elevation_level: Optional[str] = Field(None, alias="elevationLevel")
    scope: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class UserIdentity(BaseModel):
    """User identity configuration"""
    auto_user: Optional[AutoUser] = Field(None, alias="autoUser")

    model_config = ConfigDict(populate_by_name=True)


class TaskConstraints(BaseModel):
    """Task constraint settings"""
    max_task_retry_count: Optional[int] = Field(None, alias="maxTaskRetryCount")
    max_wall_clock_time: Optional[str] = Field(None, alias="maxWallClockTime")
    retention_time: Optional[str] = Field(None, alias="retentionTime")

    model_config = ConfigDict(populate_by_name=True)


class ContainerInfo(BaseModel):
    """Container execution information"""
    container_id: Optional[str] = Field(None, alias="containerId")
    state: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ExecutionInfo(BaseModel):
    """Task execution information"""
    container_info: Optional[ContainerInfo] = Field(None, alias="containerInfo")
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    exit_code: Optional[int] = Field(None, alias="exitCode")
    retry_count: Optional[int] = Field(None, alias="retryCount")
    requeue_count: Optional[int] = Field(None, alias="requeueCount")
    result: Optional[str] = None
    pool_id: Optional[str] = Field(None, alias="poolId")

    model_config = ConfigDict(populate_by_name=True)


class ContainerSettings(BaseModel):
    """Container configuration for task"""
    image_name: Optional[str] = Field(None, alias="imageName")
    container_run_options: Optional[str] = Field(None, alias="containerRunOptions")
    working_directory: Optional[str] = Field(None, alias="workingDirectory")

    model_config = ConfigDict(populate_by_name=True)


class NodeInfo(BaseModel):
    """Node information where task ran"""
    node_id: Optional[str] = Field(None, alias="nodeId")
    node_url: Optional[str] = Field(None, alias="nodeUrl")
    pool_id: Optional[str] = Field(None, alias="poolId")
    affinity_id: Optional[str] = Field(None, alias="affinityId")
    task_root_directory: Optional[str] = Field(None, alias="taskRootDirectory")
    task_root_directory_url: Optional[str] = Field(None, alias="taskRootDirectoryUrl")

    model_config = ConfigDict(populate_by_name=True)


class ResourceFile(BaseModel):
    """Resource file for task"""
    file_path: Optional[str] = Field(None, alias="filePath")
    http_url: Optional[str] = Field(None, alias="httpUrl")

    model_config = ConfigDict(populate_by_name=True)


class ContainerDestination(BaseModel):
    """Container destination for output files"""
    container_url: Optional[str] = Field(None, alias="containerUrl")
    path: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class OutputFileDestination(BaseModel):
    """Destination for output files"""
    container: Optional[ContainerDestination] = None

    model_config = ConfigDict(populate_by_name=True)


class OutputFileUploadOptions(BaseModel):
    """Upload options for output files"""
    upload_condition: Optional[str] = Field(None, alias="uploadCondition")

    model_config = ConfigDict(populate_by_name=True)


class OutputFile(BaseModel):
    """Output file specification"""
    file_pattern: Optional[str] = Field(None, alias="filePattern")
    destination: Optional[OutputFileDestination] = None
    upload_options: Optional[OutputFileUploadOptions] = Field(None, alias="uploadOptions")

    model_config = ConfigDict(populate_by_name=True)


class TaskModel(BaseModel):
    """Azure Batch Task"""
    id: str
    state: str
    previous_state: Optional[str] = Field(None, alias="previousState")
    creation_time: datetime = Field(..., alias="creationTime")
    last_modified: datetime = Field(..., alias="lastModified")
    state_transition_time: datetime = Field(..., alias="stateTransitionTime")
    previous_state_transition_time: Optional[datetime] = Field(None, alias="previousStateTransitionTime")
    e_tag: str = Field(..., alias="eTag")
    url: str
    command_line: str = Field(..., alias="commandLine")
    constraints: Optional[TaskConstraints] = None
    container_settings: Optional[ContainerSettings] = Field(None, alias="containerSettings")
    execution_info: Optional[ExecutionInfo] = Field(None, alias="executionInfo")
    node_info: Optional[NodeInfo] = Field(None, alias="nodeInfo")
    resource_files: Optional[List[ResourceFile]] = Field(None, alias="resourceFiles")
    output_files: Optional[List[OutputFile]] = Field(None, alias="outputFiles")
    required_slots: Optional[int] = Field(None, alias="requiredSlots")
    user_identity: Optional[UserIdentity] = Field(None, alias="userIdentity")
    raw: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_az(cls, data: Dict[str, Any]) -> "TaskModel":
        """Create Task from Azure CLI data"""
        return cls(**data, raw=data)


class JobConstraints(BaseModel):
    """Job constraint settings"""
    max_task_retry_count: Optional[int] = Field(None, alias="maxTaskRetryCount")
    max_wall_clock_time: Optional[str] = Field(None, alias="maxWallClockTime")

    model_config = ConfigDict(populate_by_name=True)


class PoolInfo(BaseModel):
    """Pool information for job"""
    pool_id: Optional[str] = Field(None, alias="poolId")

    model_config = ConfigDict(populate_by_name=True)


class JobExecutionInfo(BaseModel):
    """Job execution information"""
    pool_id: Optional[str] = Field(None, alias="poolId")
    start_time: Optional[datetime] = Field(None, alias="startTime")

    model_config = ConfigDict(populate_by_name=True)


class JobModel(BaseModel):
    """Azure Batch Job"""
    id: str
    state: str
    creation_time: datetime = Field(..., alias="creationTime")
    last_modified: datetime = Field(..., alias="lastModified")
    state_transition_time: datetime = Field(..., alias="stateTransitionTime")
    e_tag: str = Field(..., alias="eTag")
    url: str
    display_name: Optional[str] = Field(None, alias="displayName")
    priority: Optional[int] = None
    allow_task_preemption: Optional[bool] = Field(None, alias="allowTaskPreemption")
    max_parallel_tasks: Optional[int] = Field(None, alias="maxParallelTasks")
    uses_task_dependencies: Optional[bool] = Field(None, alias="usesTaskDependencies")
    constraints: Optional[JobConstraints] = None
    pool_info: PoolInfo = Field(..., alias="poolInfo")
    execution_info: Optional[JobExecutionInfo] = Field(None, alias="executionInfo")
    on_all_tasks_complete: Optional[str] = Field(None, alias="onAllTasksComplete")
    on_task_failure: Optional[str] = Field(None, alias="onTaskFailure")
    raw: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_az(cls, data: Dict[str, Any]) -> "JobModel":
        """Create Job from Azure CLI data"""
        return cls(**data, raw=data)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC timezone"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
