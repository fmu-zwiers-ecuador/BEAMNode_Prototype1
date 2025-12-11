# JSON FORMAT OUTLINE:
{
  "node_id": "node_id",
  "sensor": "sensor_used",
  "enabled" : [true/false], ---- Boolean value, dictates whether sensor is enabled
  "frequency" : [int minutes] ---- Dictates how often the sensor is run, in minutes
  ## Next step will vary depending on sensor used, keep syntax ('{}'s and '[]'s) consistent. ##
  "records" : [
    {
        "timestamp" : "time_recorded",
        "data1" : "data_recorded",
        "data2" : "data_recorded"
        
    },
    {
        "timestamp" : "time_recorded",
        "data1" : "data_recorded",
        "data2" : "data_recorded"
    }
  ]
}