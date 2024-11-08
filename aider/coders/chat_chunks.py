from dataclasses import dataclass, field
from typing import List


@dataclass
class ChatChunks:
    system: List = field(default_factory=list)
    examples: List = field(default_factory=list)
    done: List = field(default_factory=list)
    repo: List = field(default_factory=list)
    readonly_files: List = field(default_factory=list)
    chat_files: List = field(default_factory=list)
    cur: List = field(default_factory=list)
    reminder: List = field(default_factory=list)

    def all_messages(self):
        return (
            self.system
            + self.examples
            + self.readonly_files
            + self.repo
            + self.done
            + self.chat_files
            + self.cur
            + self.reminder
        )

    def wrap_xml(self, tag, content):
        """Wrap content in XML tags"""
        if not content:
            return ""
        return f"<{tag}>{content}</{tag}>"

    def format_xml_messages(self):
        """Format all message chunks as XML"""
        xml = []
        
        # System context
        if self.system:
            xml.append(self.wrap_xml("system_context", self.system[-1]["content"]))
            
        # Repository map
        if self.repo:
            xml.append(self.wrap_xml("repository_map", self.repo[-1]["content"]))
            
        # Project files
        if self.chat_files:
            xml.append(self.wrap_xml("project_files", self.chat_files[-1]["content"]))
            
        # Read-only files  
        if self.readonly_files:
            xml.append(self.wrap_xml("readonly_files", self.readonly_files[-1]["content"]))
            
        # Instructions
        if self.reminder:
            xml.append(self.wrap_xml("instructions", self.reminder[-1]["content"]))
            
        # Current messages
        if self.cur:
            xml.append(self.wrap_xml("current_messages", self.cur[-1]["content"]))
            
        return "\n".join(xml)

    def add_cache_control_headers(self):
        if self.examples:
            self.add_cache_control(self.examples)
        else:
            self.add_cache_control(self.system)

        if self.repo:
            # this will mark both the readonly_files and repomap chunk as cacheable
            self.add_cache_control(self.repo)
        else:
            # otherwise, just cache readonly_files if there are any
            self.add_cache_control(self.readonly_files)

        self.add_cache_control(self.chat_files)

    def add_cache_control(self, messages):
        if not messages:
            return

        content = messages[-1]["content"]
        if type(content) is str:
            content = dict(
                type="text",
                text=content,
            )
        content["cache_control"] = {"type": "ephemeral"}

        messages[-1]["content"] = [content]

    def cacheable_messages(self):
        messages = self.all_messages()
        for i, message in enumerate(reversed(messages)):
            if isinstance(message.get("content"), list) and message["content"][0].get(
                "cache_control"
            ):
                return messages[: len(messages) - i]
        return messages
