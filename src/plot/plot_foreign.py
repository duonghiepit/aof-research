import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def candle_stick_df(df,
                    title=None,
                    xlab='Date', ylab='Price',
                    colors=['blue', 'red'],
                    width=800, height=600,
                    show_advanced=['volume', 'macd', 'rsi'],
                    **kwargs):
    """
    Vẽ biểu đồ nến (candlestick) kèm theo các chỉ báo nâng cao từ một DataFrame.
    
    DF phải chứa các cột:
        - 'Date' (sẽ được set làm index nếu có),
        - 'Open', 'High', 'Low', 'Close' và (nếu có) 'Volume'
    
    Các chỉ báo nâng cao hỗ trợ:
        - 'volume': Khối lượng giao dịch.
        - 'macd': Bao gồm MACD line, Signal line và Histogram.
        - 'rsi': Chỉ số RSI (với đường quá mua 70 và quá bán 30).
    
    Hàm sẽ tự động chuyển các cột ['Open', 'High', 'Low', 'Close', 'Volume'] thành chữ thường.
    Đồng thời, hàm sẽ chia layout subplot tùy theo số chỉ báo nâng cao cần vẽ và thêm ghi chú tên
    của từng chỉ báo trên plot.
    
    Returns:
        fig: Đối tượng Plotly Figure.
    """

    # Nếu DataFrame có cột 'Date', set nó làm index và chuyển sang Datetime
    if 'Date' in df.columns:
        df = df.copy()
        df.set_index('Date', inplace=True)
    try:
        df.index = pd.to_datetime(df.index)
    except Exception as e:
        raise ValueError("Index của DataFrame phải chuyển đổi được sang Datetime!")

    # Đổi tên các cột cần thiết thành chữ thường
    rename_map = {
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }
    df.rename(columns=rename_map, inplace=True)

    # Kiểm tra các cột cần thiết cho biểu đồ nến
    required_cols = ['open', 'high', 'low', 'close']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"DataFrame phải chứa cột '{col}'!")

    # Nếu tiêu đề chưa có, thiết lập mặc định
    if title is None:
        title = "Stock Price & Advanced Metrics"

    # Xác định layout subplot theo số chỉ báo nâng cao
    num_adv = len(show_advanced)
    # Trường hợp đặc biệt cho 3 chỉ báo (volume, macd, rsi)
    if sorted(show_advanced) == ['macd', 'rsi', 'volume']:
        row_heights = [0.3, 0.3, 0.15, 0.15]
        r_price, r_volume, r_macd, r_rsi = 1, 2, 3, 4
    # Nếu chỉ 1 chỉ báo
    elif num_adv == 1:
        if 'volume' in show_advanced:
            row_heights = [0.6, 0.4]
            r_price, r_volume = 1, 2
            r_macd, r_rsi = None, None
        elif 'macd' in show_advanced:
            row_heights = [0.6, 0.4]
            r_price, r_macd = 1, 2
            r_volume, r_rsi = None, None
        elif 'rsi' in show_advanced:
            row_heights = [0.6, 0.4]
            r_price, r_rsi = 1, 2
            r_volume, r_macd = None, None
    # Nếu 2 chỉ báo
    elif num_adv == 2:
        # Xét các trường hợp riêng
        if sorted(show_advanced) == ['macd', 'rsi']:
            row_heights = [0.6, 0.4]
            r_price, r_rsi = 1, 2
            r_macd = None  # Bạn có thể kết hợp MACD và RSI trên cùng 1 subplot nếu muốn,
                           # hoặc chia 3 hàng như sau: [0.5, 0.3, 0.2]
        elif sorted(show_advanced) == ['macd', 'volume']:
            row_heights = [0.5, 0.3, 0.2]
            r_price, r_volume, r_macd = 1, 2, 3
            r_rsi = None
        elif sorted(show_advanced) == ['rsi', 'volume']:
            row_heights = [0.5, 0.3, 0.2]
            r_price, r_volume, r_rsi = 1, 2, 3
            r_macd = None
        else:
            row_heights = [0.5, 0.3, 0.2]
            r_price = 1
            r_volume = 2
            r_macd = None
            r_rsi = None
    # Nếu không có chỉ báo nâng cao
    else:
        row_heights = [1.0]
        r_price = 1
        r_volume, r_macd, r_rsi = None, None, None

    total_rows = len(row_heights)
    fig = make_subplots(rows=total_rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=row_heights)

    # Thêm trace Candlestick cho giá
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        increasing_line_color=colors[0],
        decreasing_line_color=colors[1],
        name='Price'
    ), row=r_price, col=1)
    
    # Thêm annotation cho giá (Price)
    fig.add_annotation(
        xref="paper", yref=f"y{r_price}",
        x=0, y=1,
        text="Price",
        showarrow=False,
        font=dict(size=14, color="black")
    )

    # Thêm Volume nếu có
    if 'volume' in show_advanced and r_volume is not None and 'volume' in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            marker=dict(color='red'),
            name='Volume'
        ), row=r_volume, col=1)
        fig.add_annotation(
            xref="paper", yref=f"y{r_volume}",
            x=0, y=1,
            text="Volume",
            showarrow=False,
            font=dict(size=14, color="black")
        )

    # Thêm MACD nếu có
    if 'macd' in show_advanced and r_macd is not None:
        ema12 = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
        ema26 = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False, min_periods=9).mean()
        macd_hist = macd_line - macd_signal

        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd_line,
            line=dict(color='#ff9900', width=1),
            name='MACD'
        ), row=r_macd, col=1)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd_signal,
            line=dict(color='#000000', width=1),
            name='Signal'
        ), row=r_macd, col=1)
        colors_hist = np.where(macd_hist < 0, '#000', '#ff9900')
        fig.add_trace(go.Bar(
            x=df.index,
            y=macd_hist,
            name='Histogram',
            marker_color=colors_hist
        ), row=r_macd, col=1)
        fig.add_annotation(
            xref="paper", yref=f"y{r_macd}",
            x=0, y=1,
            text="MACD",
            showarrow=False,
            font=dict(size=14, color="black")
        )

    # Thêm RSI nếu có
    if 'rsi' in show_advanced and r_rsi is not None:
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=rsi,
            line=dict(width=1),
            name='RSI'
        ), row=r_rsi, col=1)
        # Thêm đường giới hạn cho RSI (70 & 30)
        fig.add_hline(
            y=70,
            line_dash="dot",
            row=r_rsi,
            col="all",
            annotation_text="70% (Overbought)",
            annotation_position="bottom right"
        )
        fig.add_hline(
            y=30,
            line_dash="dot",
            row=r_rsi,
            col="all",
            annotation_text="30% (Oversold)",
            annotation_position="bottom right"
        )
        fig.add_annotation(
            xref="paper", yref=f"y{r_rsi}",
            x=0, y=1,
            text="RSI",
            showarrow=False,
            font=dict(size=14, color="black")
        )

    # Cập nhật layout tổng thể
    fig.update_layout(
        title=title,
        width=width,
        height=height,
        showlegend=True,
        font=dict(color='red'),
        plot_bgcolor='white',
        xaxis=dict(
            title=dict(
                text=f'<b>{xlab}</b>',
                font=dict(size=20, color='green')
            ),
            tickfont=dict(color='yellow')
        ),
        yaxis=dict(
            title=dict(
                text=f'<b>{ylab}</b>',
                font=dict(size=20, color='green')
            ),
            tickfont=dict(color='yellow')
        )
    )
    
    return fig
