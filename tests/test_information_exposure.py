import json
import runpy
import sys
import unittest
from contextlib import nullcontext
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, mock_open, patch


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "Codecademy" / "Agents"
CHAT_APPS = (
    AGENTS / "Streamlit_Agent" / "Chatbot.py",
    AGENTS / "Augmented_Writing_App" / "main.py",
)
RAG_APP = ROOT / "Codecademy" / "RAG" / "app.py"
PRIVATE = "PRIVATE_SENTINEL: credential and internal path"


class SessionState(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class StopApp(Exception):
    pass


def streamlit_stub():
    st = ModuleType("streamlit")
    st.session_state = SessionState()
    for name in (
        "title", "subheader", "markdown", "info", "error", "write", "json",
        "text_area", "number_input", "button", "chat_input",
    ):
        setattr(st, name, Mock())
    st.sidebar = Mock()
    st.chat_message = Mock(side_effect=lambda role: nullcontext())
    st.chat_input.return_value = None
    st.text_area.return_value = "question"
    st.number_input.return_value = 2
    st.button.return_value = False
    st.stop = Mock(side_effect=StopApp)
    return st


class InformationExposureTests(unittest.TestCase):
    def run_chat(self, path, st, completion=None, initialization_error=False):
        openai = ModuleType("openai")
        openai.OpenAI = Mock(
            side_effect=RuntimeError(PRIVATE) if initialization_error else None
        )
        handler = ModuleType("tools.handler")
        handler.get_completion_with_tools = completion or Mock()
        with patch.dict(sys.modules, {
            "streamlit": st, "openai": openai, "tools": ModuleType("tools"),
            "tools.handler": handler,
        }):
            return runpy.run_path(str(path))

    def assert_no_private_output(self, st):
        for name in ("markdown", "info", "error", "write", "json"):
            self.assertNotIn(PRIVATE, str(getattr(st, name).call_args_list))
        st.info.assert_not_called()
        st.json.assert_not_called()

    def test_chat_request_errors_omit_exception_and_response(self):
        for path in CHAT_APPS:
            with self.subTest(app=path.name):
                st = streamlit_stub()
                st.chat_input.return_value = "hello"
                error = RuntimeError(PRIVATE)
                error.response = {"provider_details": PRIVATE}
                with self.assertLogs(level="ERROR") as logs:
                    self.run_chat(path, st, Mock(side_effect=error))
                st.error.assert_called_once_with(
                    "Unable to complete your request. Please try again later."
                )
                self.assert_no_private_output(st)
                self.assertNotIn(PRIVATE, str(logs.output))

    def test_chat_initialization_errors_are_safe(self):
        for path in CHAT_APPS:
            with self.subTest(app=path.name):
                st = streamlit_stub()
                with self.assertLogs(level="ERROR") as logs:
                    with self.assertRaises(StopApp):
                        self.run_chat(path, st, initialization_error=True)
                st.error.assert_called_once()
                self.assert_no_private_output(st)
                self.assertNotIn(PRIVATE, str(logs.output))

    def test_chat_success_and_rerun_hide_tool_diagnostics(self):
        for path in CHAT_APPS:
            with self.subTest(app=path.name):
                st = streamlit_stub()
                st.chat_input.return_value = "hello"
                messages = [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": PRIVATE,
                     "tool_calls": [{"function": PRIVATE}]},
                    {"role": "tool", "content": PRIVATE},
                    {"role": "assistant", "content": "Done"},
                ]
                completion = Mock(return_value=("Done", messages, {
                    "function_name": PRIVATE, "function_args": {"x": PRIVATE},
                    "result": PRIVATE,
                }))
                st.session_state.tool_calls = {0: PRIVATE}
                self.run_chat(path, st, completion)
                completion.assert_called_once()
                st.markdown.assert_any_call("Done")
                self.assertNotIn("tool_calls", st.session_state)
                self.assert_no_private_output(st)
                if path.name == "Chatbot.py":
                    self.assertEqual(st.session_state.messages, messages)
                else:
                    self.assertEqual(st.session_state.messages, [
                        messages[0], messages[3],
                    ])
                st.chat_input.return_value = None
                st.markdown.reset_mock()
                self.run_chat(path, st)
                self.assertEqual(
                    [call.args[0] for call in st.markdown.call_args_list],
                    ["hello", "Done"],
                )
                self.assert_no_private_output(st)

    def run_rag(self, st, client):
        chroma = ModuleType("chromadb")
        chroma.PersistentClient = client
        with patch.dict(sys.modules, {"streamlit": st, "chromadb": chroma}):
            runpy.run_path(str(RAG_APP))

    def test_rag_displays_documents_without_metadata(self):
        st = streamlit_stub()
        st.button.return_value = True
        collection = Mock()
        collection.query.return_value = {
            "documents": [["Approved document"]],
            "ids": [PRIVATE], "metadatas": [{"internal": PRIVATE}],
        }
        client = Mock()
        client.return_value.get_or_create_collection.return_value = collection
        self.run_rag(st, client)
        collection.query.assert_called_once_with(
            query_texts=["question"], n_results=2
        )
        st.write.assert_any_call("Approved document")
        self.assert_no_private_output(st)

    def test_rag_errors_are_safe(self):
        for initialization_error in (True, False):
            with self.subTest(initialization_error=initialization_error):
                st = streamlit_stub()
                st.button.return_value = True
                client = Mock()
                if initialization_error:
                    client.side_effect = RuntimeError(PRIVATE)
                else:
                    collection = client.return_value.get_or_create_collection.return_value
                    collection.query.side_effect = RuntimeError(PRIVATE)
                with self.assertLogs(level="ERROR") as logs:
                    with self.assertRaises(StopApp):
                        self.run_rag(st, client)
                st.error.assert_called_once()
                self.assert_no_private_output(st)
                self.assertNotIn(PRIVATE, str(logs.output))

    def test_tool_errors_are_safe_before_reaching_the_model(self):
        cases = (
            ("Augmented_Writing_App", "write_section", (1, "content")),
            ("Augmented_Writing_App", "read_section", (1,)),
            ("Augmented_Writing_App", "delete_section", (1,)),
            ("Augmented_Writing_App", "lookup_contact", ("name",)),
            ("Streamlit_Agent", "write_to_memory", ("memory",)),
            ("Streamlit_Agent", "read_from_memory", ()),
        )
        for app, function_name, args in cases:
            with self.subTest(tool=function_name):
                namespace = runpy.run_path(
                    str(AGENTS / app / "tools" / f"{function_name}.py")
                )
                with patch("os.path.exists", return_value=True), \
                     patch("builtins.open", side_effect=OSError(PRIVATE)), \
                     patch("os.remove", side_effect=OSError(PRIVATE)), \
                     self.assertLogs(level="ERROR") as logs:
                    result = namespace[function_name](*args)
                self.assertEqual(result["status"], "error")
                self.assertNotIn(PRIVATE, json.dumps(result))
                self.assertNotIn(PRIVATE, str(logs.output))

    def test_tool_success_shapes_are_preserved(self):
        cases = (
            ("Augmented_Writing_App", "write_section", (1, "content"), ""),
            ("Augmented_Writing_App", "read_section", (1,), "content"),
            ("Augmented_Writing_App", "delete_section", (1,), ""),
            ("Augmented_Writing_App", "lookup_contact", ("name",),
             '{"name": "Approved contact"}'),
            ("Streamlit_Agent", "write_to_memory", ("memory",), "[]"),
            ("Streamlit_Agent", "read_from_memory", (),
             '[{"time": "now", "memory": "Approved memory"}]'),
        )
        for app, function_name, args, data in cases:
            with self.subTest(tool=function_name):
                namespace = runpy.run_path(
                    str(AGENTS / app / "tools" / f"{function_name}.py")
                )
                with patch("os.path.exists", return_value=True), \
                     patch("builtins.open", mock_open(read_data=data)), \
                     patch("os.makedirs"), patch("os.remove"):
                    result = namespace[function_name](*args)
                self.assertEqual(result["status"], "success")
                if function_name == "read_section":
                    self.assertEqual(result["content"], "content")
                elif function_name == "lookup_contact":
                    self.assertEqual(result["description"], "Approved contact")
                elif function_name == "read_from_memory":
                    self.assertEqual(result["memories"], "now: Approved memory")


if __name__ == "__main__":
    unittest.main()
