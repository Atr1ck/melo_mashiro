import time
from melobot.protocols.onebot.v11 import Adapter, ImageSegment, on_message, MessageEvent
from melobot.utils.parse import CmdParser, CmdArgs
from bestdori.cards import get_card
from bestdori.player import get_player
from bestdori.tracker import get_now_event

@on_message(parser=CmdParser(
    cmd_start=[".", "/"],
    cmd_sep=[" "],
    targets=["bandori_card"]
))
async def bandori_cards(adapter: Adapter, event: MessageEvent, args: CmdArgs):
    """
    .bandori_card id img_type card_type
    """
    try:
        print("正在获取图片")
        card = await get_card(args.vals[0])

        match args.vals[1]:
            case "full":
                img = ImageSegment(file=await card.get_full_image(args.vals[2]))
            case "thumb":
                img = ImageSegment(file=await card.get_thumb_image(args.vals[2]))
            case "character":
                img = ImageSegment(file=await card.get_character_image(args.vals[2]))
            case "livesd":
                img = ImageSegment(file= await card.get_livesd())
            case _:
                await adapter.send("参数错误")
    
        await adapter.send(img)
    except:
        await adapter.send("发生错误")

@on_message(parser=CmdParser(
    cmd_start=[".", "/"],
    cmd_sep=[" "],
    targets=["bandori_player"]
))
async def bandori_player(adapter: Adapter, event: MessageEvent, args: CmdArgs):
    """
    .bandori_player id
    """
    start_time = time.time()
    print(f"正在获取玩家信息: {args.vals[0]}")
    player = await get_player(id=args.vals[0])
    if player == "Unvalid Data":
        await adapter.send("信息获取失败")
    else:
        print("已获取玩家信息，绘制图片")
        base64_str = await player.player_dataImg()
        img = ImageSegment(file=base64_str)
        await adapter.send(img)
        end_time2 = time.time()
        print("time:", end_time2 - start_time)

@on_message(parser=CmdParser(
    cmd_start = [".", "/"],
    cmd_sep = [" "],
    targets=["bandori_event"]
))
async def bandori_event(adapter: Adapter, event: MessageEvent, args: CmdArgs):
    """
    .bandori_event tier
    """
    print("正在获取活动分数信息")
    image_base64 = await get_now_event(tier=args.vals[0])
    image = ImageSegment(file=image_base64)
    await adapter.send(image)