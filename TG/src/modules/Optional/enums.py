from enum import Enum

class ProductColumn(str, Enum):
    NAME = 'name'
    PRICE = 'price'
    CAPACITY = 'capacity'
    SPEED = 'speed'
    MIN_TEMP = "min_temp"
    MAX_TEMP = "max_temp"
    TYPE = 'type'

class FilterOperator(str, Enum):
    EQUAL = '='
    GREATER = '>'
    LESS = '<'
    GREATER_EQUAL = '>='
    LESS_EQUAL = '<='
    LIKE = "LIKE"
    IN = "IN"