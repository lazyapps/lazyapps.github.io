"""Remove the two bicycle supports without touching either wheel or its road."""


def wheel_support_filter(input_label='0:v', output_label='clean'):
    filters = [f'[{input_label}]split=3[base][left][right]']
    for side, x, axle, start, slope, donor in [
        ('left', 80, 139, 106, -16, 'mod(X,5)'),
        ('right', 360, 342, 370, 13, 'W-1-mod(X,5)'),
    ]:
        # Keep the round rim; replace only the narrow diagonal below it with
        # nearby pixels on the same road row, preserving horizontal hatching.
        mask = (f'gt((X+{x}-{axle})^2+(Y+54)^2,69^2)'
                f'*lt(abs(X+{x}-({start}+(Y-4)*{slope}/22)),7)*between(Y,3,29)')
        expression = f'if({mask},p({donor},Y),p(X,Y))'
        filters.append(f'[{side}]crop=40:32:{x}:448,format=yuv444p,'
                       f"geq=lum='{expression}':cb='{expression}':cr='{expression}'[{side}fix]")
    filters.extend([
        '[base][leftfix]overlay=80:448:format=auto[mid]',
        f'[mid][rightfix]overlay=360:448:format=auto,format=yuv420p[{output_label}]',
    ])
    return ';'.join(filters)
