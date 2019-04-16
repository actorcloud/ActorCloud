<template>
  <div class="code-editor">
    <textarea ref="textarea"></textarea>
  </div>
</template>


<script>
/* eslint-disable */
import CodeMirror from 'codemirror'
import 'codemirror/addon/lint/lint.css'
import 'codemirror/lib/codemirror.css'
import 'codemirror/theme/lesser-dark.css'
import 'codemirror/theme/dracula.css'
require('script-loader!jsonlint')
import 'codemirror/mode/javascript/javascript'
import 'codemirror/mode/python/python'
import 'codemirror/mode/sql/sql'
import 'codemirror/addon/lint/lint'
import 'codemirror/addon/lint/json-lint'

export default {
  name: 'code-editor',

  props: {
    value: {
      required: true,
    },
    lang: {
      type: String,
      required: true,
    },
    theme: {
      type: String,
      default: null,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    height: {
      type: String,
      default: '200px',
    },
    lineNumbers: {
      type: Boolean,
      default: true,
    }
  },

  data() {
    return {
      codeEditor: false
    }
  },

  computed: {
    currentTheme() {
      return this.$store.state.accounts.currentTheme
    },
  },

  watch: {
    value(value) {
      const editorValue = this.codeEditor.getValue()
      if (value !== editorValue) {
        this.codeEditor.setValue(this.value)
      }
    },
    disabled() {
      this.codeEditor.setOption('readOnly', this.disabled)
    },
    currentTheme() {
      const newTheme = this.theme || this.getTheme()
      this.codeEditor.setOption('theme', newTheme)
    },
  },

  methods: {
    initEditorption() {
      this.codeEditor = CodeMirror.fromTextArea(this.$refs.textarea, {
        lineNumbers: this.lineNumbers,
        mode: this.lang,
        gutters: ['CodeMirror-lint-markers'],
        theme: this.theme || this.getTheme(),
        lint: true,
        readOnly: this.disabled,
      })
      this.codeEditor.setSize('auto', this.height)
      this.codeEditor.setValue(this.value)
      this.codeEditor.on('change', cm => {
        this.$emit('changed', cm.getValue())
        this.$emit('input', cm.getValue())
      })
    },

    getValue() {
      return this.codeEditor.getValue()
    },

    getTheme() {
      let theme = 'default'
      const langTheme = {
        'python': 'dracula',
        'text/x-sql': 'dracula',
        'application/json': 'lesser-dark',
      }
      if (this.currentTheme === 'dark' && langTheme[this.lang]) {
        return langTheme[this.lang]
      }
      return theme
    },
  },

  mounted() {
    this.initEditorption()
  },
}
</script>


<style scoped>
.code-editor{
  height: 100%;
  position: relative;
}
.code-editor >>> .cm-s-rubyblue span.cm-string {
  color: #F08047;
}
</style>
