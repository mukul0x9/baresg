import re


class Template:
    def __init__(self, template_str: str):
        self.template_str = template_str
        self.compiled_code = self._compile_template(template_str)

    def _compile_template(self, template: str) -> str:
        tokens = re.split(r"({{.*?}}|{%.*?%})", template)

        code = []
        code.append("def render_template(context):")
        code.append("    result = []")

        indent = "    "
        scope_track = []

        def resolve_scope(context_var: str) -> str:
            parts = context_var.split(".")
            root = parts[0]

            if root in scope_track:
                final = root
            else:
                final = f'context["{root}"]'

            for p in parts[1:]:
                final += f"['{p}']"

            return final

        for token in tokens:
            if token.startswith("{{"):
                var = token[2:-2].strip()
                final = resolve_scope(var)
                code.append(f"{indent}result.append(str({final}))")

            elif token.startswith("{%"):
                tag = token[2:-2].strip()

                if tag.startswith("if "):
                    condition = tag[3:].strip()
                    final = resolve_scope(condition)
                    code.append(f"{indent}if {final}:")
                    indent += "    "

                elif tag.startswith("elif "):
                    indent = indent[:-4]
                    condition = tag[5:].strip()
                    final = resolve_scope(condition)
                    code.append(f"{indent}elif {final}:")
                    indent += "    "

                elif tag.startswith("else"):
                    indent = indent[:-4]
                    code.append(f"{indent}else:")
                    indent += "    "

                elif tag.startswith("endif"):
                    indent = indent[:-4]

                elif tag.startswith("for "):
                    parts = tag.split()
                    loop_var = parts[1]
                    context_var = parts[3]

                    final = resolve_scope(context_var)

                    code.append(f"{indent}for {loop_var} in {final}:")
                    indent += "    "
                    scope_track.append(loop_var)

                elif tag.startswith("endfor"):
                    indent = indent[:-4]
                    if scope_track:
                        scope_track.pop()

            else:
                if token:
                    code.append(f"{indent}result.append({repr(token)})")

        code.append(f'{indent}return "".join(result)')

        return "\n".join(code)

    def render(self, context: dict) -> str:
        safe_builtins = {
            "str": str,
            "int": int,
            "len": len,
            "range": range,
            "enumerate": enumerate,
        }

        safe_namespace = {"__builtins__": safe_builtins}

        try:
            exec(self.compiled_code, safe_namespace)
            render_func = safe_namespace["render_template"]
            return render_func(context)  # type: ignore

        except Exception as e:
            print("Template Error:\n")
            print(self.compiled_code)
            raise e
