module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    'plugin:vue/essential',
    '@vue/airbnb',
  ],
  rules: {
    semi: 0,
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-shadow': 0,
    'no-param-reassign': 0,
    'new-cap': 0,
    'consistent-return': 0,
    'import/no-extraneous-dependencies': [2, { devDependencies: true }],
    'import/extensions': ['error', 'always', {
      js: 'never',
      vue: 'never',
    }],
    'object-curly-newline': 0,
    'arrow-body-style': 0,
    'prefer-destructuring': 0,
    'no-tabs': 0,
    'vue/no-use-v-if-with-v-for': 0,
    'max-len': [2, { code: 150, ignoreUrls: true, ignoreStrings: true, ignoreTemplateLiterals: true }],
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
}
