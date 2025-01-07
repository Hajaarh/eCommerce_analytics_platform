def get_rfm_pipeline():
    return [
        {
            '$project': {
                'Customer ID': 1,
                'Order Date': 1,
                'Sales': 1,
                '_id': 0
            }
        },
        {
            '$group': {
                '_id': '$Customer ID',
                'last_purchase': {'$max': '$Order Date'},
                'total_sales': {'$sum': '$Sales'},
                'frequency': {'$sum': 1}
            }
        }
    ]

def get_sales_by_date_pipeline():
    return [
        {
            '$group': {
                '_id': '$Order Date',
                'total_ventes': {
                    '$sum': '$Sales'
                }
            }
        },
        {
            '$sort': {
                '_id': 1
            }
        }]

def get_base_lookup_pipeline():
    return [
        {
            '$lookup': {
                'from': 'Customers',
                'localField': 'Customer ID',
                'foreignField': 'Customer ID',
                'as': 'customer_details'
            }
        },
        {
            '$lookup': {
                'from': 'Products',
                'localField': 'Product ID',
                'foreignField': 'Product ID',
                'as': 'product_details'
            }
        },
        {
            '$lookup': {
                'from': 'Location',
                'localField': 'Postal Code',
                'foreignField': 'Postal Code',
                'as': 'location_details'
            }
        },
        {'$unwind': '$customer_details'},
        {'$unwind': '$product_details'},
        {'$unwind': '$location_details'}
    ]

def get_total_sales_pipeline():
    return [
        {'$group': {'_id': None, 'total_sales': {'$sum': '$Sales'}}}
    ]

def get_sales_by_state_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$location_details.State',
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]

def get_sales_by_category_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Category',
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]

def get_sales_by_product_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Product Name',
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]


def get_total_profit_pipeline():
    return [
        {'$group': {'_id': None, 'total_profit': {'$sum': '$Profit'}}}
    ]

def get_profit_by_category_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Category',
                'total_profit': {'$sum': '$Profit'}
            }
        },
        {'$sort': {'total_profit': -1}}
    ]

def get_profit_by_product_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Product Name',
                'total_profit': {'$sum': '$Profit'}
            }
        },
        {'$sort': {'total_profit': -1}}
    ]

def get_top_profitable_products_pipeline(limit=5):
    return get_profit_by_product_pipeline() + [{'$limit': limit}]

def get_average_basket_pipeline():

        return [
            {
                '$group': {
                    '_id': None,
                    'total_sales': {'$sum': '$Sales'},
                    'order_count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'average_basket': {'$divide': ['$total_sales', '$order_count']}
                }
            }
        ]

def get_average_basket_by_state_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$location_details.State',
                'total_sales': {'$sum': '$Sales'},
                'order_count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 1,
                'average_basket': {'$divide': ['$total_sales', '$order_count']}
            }
        },
        {'$sort': {'average_basket': -1}}
    ]

def get_average_basket_by_category_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Category',
                'total_sales': {'$sum': '$Sales'},
                'order_count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 1,
                'average_basket': {'$divide': ['$total_sales', '$order_count']}
            }
        },
        {'$sort': {'average_basket': -1}}
    ]


def get_sales_by_location_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': {
                    'state': '$location_details.State',
                    'city': '$location_details.City'
                },
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]

def get_sales_by_region_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$location_details.Region',
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]

def get_average_basket_by_region_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': {
                    'region': '$location_details.Region',
                    'order': '$Order ID'
                },
                'basket_value': {'$sum': '$Sales'}
            }
        },
        {
            '$group': {
                '_id': '$_id.region',
                'average_basket': {'$avg': '$basket_value'}
            }
        },
        {'$sort': {'average_basket': -1}}
    ]


def get_top_categories_pipeline(limit=5):
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Category',
                'total_quantity': {'$sum': '$Quantity'},
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_quantity': -1}},
        {'$limit': limit}
    ]

def get_top_products_by_quantity_pipeline(limit=5):
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': '$product_details.Product Name',
                'total_quantity': {'$sum': '$Quantity'}
            }
        },
        {'$sort': {'total_quantity': -1}},
        {'$limit': limit}
    ]

def get_sales_matrix_pipeline():
    return get_base_lookup_pipeline() + [
        {
            '$group': {
                '_id': {
                    'product': '$product_details.Product Name',
                    'region': '$location_details.Region'
                },
                'total_sales': {'$sum': '$Sales'}
            }
        },
        {'$sort': {'total_sales': -1}}
    ]


def get_date_match_stage(start_date, end_date, date_filter):
    date_formats = {
        "Jour": "%Y-%m-%d",
        "Mois": "%Y-%m",
        "Trimestre": "%Y-Q%q",
        "Année": "%Y"
    }

    return {
        '$match': {
            'Order Date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
    }


def get_metric_field(metric):
    metric_mapping = {
        "Montant total": "$Sales",
        "Quantité vendue": "$Quantity",
        "Profits": "$Profit"
    }
    return metric_mapping[metric]


def get_sales_pipeline(start_date, end_date, date_filter, metric):
    metric_field = get_metric_field(metric)
    return [
        get_date_match_stage(start_date, end_date, date_filter),
        get_base_lookup_pipeline(),
        {
            '$group': {
                '_id': '$region',
                'value': {'$sum': metric_field}
            }
        }
        ]