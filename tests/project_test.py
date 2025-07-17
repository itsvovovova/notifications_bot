from unittest.mock import AsyncMock, patch, ANY
from pytest import fixture, mark
from src.api.handlers import handler_start, handler_score, middleware_function
from src.consumer.parser import check_updates


@fixture(scope="module")
def message():
    message = AsyncMock()
    message.chat.id = 123
    return message

@mark.asyncio
async def test_start(message) -> None:
    message.text = "/start"
    mock_function = AsyncMock(return_value="Привет! Тебе нужно залогиниться в ЛК. Напиши, пожалуйста, свой логин")
    with patch("src.api.handlers.register_user", mock_function) as mock_register:
        with patch("src.api.handlers.bot.send_message", new_callable=AsyncMock) as mock_send_message:
            await handler_start(message)
            mock_register.assert_awaited_once_with(message.chat.id, ANY)
            mock_send_message.assert_awaited_once_with(message.chat.id, "Привет! Тебе нужно залогиниться в ЛК. Напиши, пожалуйста, свой логин")

@mark.asyncio
async def test_score(message) -> None:
    message.text = "/score"
    mock_function = AsyncMock(return_value="Average score: 2.00")
    with patch("src.api.handlers.get_state", return_value="accepted"):
        with patch("src.api.handlers.get_score", mock_function) as mock_score:
            with patch("src.api.handlers.bot.send_message", new_callable=AsyncMock) as mock_send_message:
                await handler_score(message)
                mock_score.assert_awaited_once_with(message.chat.id, ANY)
                mock_send_message.assert_awaited_once_with(message.chat.id, ANY)

@mark.parametrize("state, expected", [("login", "handler_login_user"),("password", "handler_password_user"),("accepted", "handler"),
])
@mark.asyncio
async def test_middleware(state, expected, message):
    handler = AsyncMock()
    with (
        patch("src.api.handlers.get_state", return_value=state),
        patch("src.api.handlers.AsyncSessionLocal"),
        patch("src.api.handlers.handler_login_user", new_callable=AsyncMock) as mock_login,
        patch("src.api.handlers.handler_password_user", new_callable=AsyncMock) as mock_pass,
        patch("src.api.handlers.bot.send_message", new_callable=AsyncMock),
    ):
        wrapped = middleware_function(handler)
        await wrapped(message)
        if state == "accepted":
            handler.assert_awaited_once_with(message)
            mock_login.assert_not_called()
            mock_pass.assert_not_called()
        elif state == "login":
            mock_login.assert_awaited_once_with(message)
            handler.assert_not_called()
        elif state == "password":
            mock_pass.assert_awaited_once_with(message)
            handler.assert_not_called()
@mark.asyncio
async def test_check_updates_detects_change():
    old_data = {"Math": 3, "Physics": 5}
    new_data = {"Math": 4, "Physics": 5}

    with patch("src.consumer.parser.get_objects", AsyncMock(return_value=old_data)):
        result = await check_updates(chat_id=123, new_data=new_data)
        assert result == {"Math": (3, 4)}