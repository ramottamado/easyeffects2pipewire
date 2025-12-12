def create_links(data: list[str]) -> list[dict[str, str]]:
    """
    Create links & plugin orders settings.

    :param data: list of plugins
    :type data: list[str]
    :return: links settings
    :rtype: list[dict[str, str]]
    """

    links_channel_left = [
        {
            "output": f"{plugin[0]}:out_l",
            "input": f"{plugin[1]}:in_l",
        }
        for plugin in list(zip(data, data[1:]))
    ]

    links_channel_right = [
        {
            "output": f"{plugin[0]}:out_r",
            "input": f"{plugin[1]}:in_r",
        }
        for plugin in list(zip(data, data[1:]))
    ]

    return links_channel_left + links_channel_right


def create_inputs(data: list[str]) -> list[str]:
    """
    Create inputs settings.

    :param data: list of plugins
    :type data: list[str]
    :return: inputs settings
    :rtype: list[str]
    """

    return [
        f"{data[0]}:in_l",
        f"{data[0]}:in_r",
    ]


def create_outputs(data: list[str]) -> list[str]:
    """
    Create outputs settings.

    :param data: list of plugins
    :type data: list[str]
    :return: outputs settings
    :rtype: list[str]
    """

    return [
        f"{data[-1]}:out_l",
        f"{data[-1]}:out_r",
    ]
