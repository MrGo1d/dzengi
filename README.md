# dzengi
This project is for trading on the dzengi.by platform

First we must to create instance of the class Trade:

trade = Trade(api_key, secret_key)

# To place a purchase order
purchase = trade.CreateOrder(
    symbol="Gold", 
    side="BUY",
    type_="LIMIT",
    quantity=0.1,
    price=3000.00,
    leverage=5
    )

# For edit order
edit = trade.LeverageOrdersEdit(
    order_id="28601567-1e55-311e-0000-00008087365c",
    new_price=2950.00,
    take_profit=3500.00
)

# For cancel order
cancel = trade.CencelOrder(
    order_id="28601567-1e55-311e-0000-00008087365c", 
    symbol="Gold"
    )


# For edit trading position
edit_trading = trade.LeverageTradeEdit(
        position_id='2854ed76-1e15-549e-0000-0000808b0005', #it's param id 
        take_profit=38.28
)

# Close trading position
close = trade.TradingPositionClose(
    position_id="28601567-1e55-311e-0000-00008087365b"
)

