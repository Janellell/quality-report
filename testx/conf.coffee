exports.config =
  directConnect: true
  specs: ['spec/*']

  capabilities:
    browserName: 'firefox'
    shardTestFiles: false
    maxInstances: 5
    chromeOptions:
      args: ["--no-sandbox", "--headless", "--disable-gpu", "--window-size=1024,800"]

  framework: 'jasmine'
  jasmineNodeOpts:
    silent: true
    defaultTimeoutInterval: 300000
    includeStackTrace: false

  baseUrl: 'http://localhost:2015'

  onPrepare: ->
    require 'testx'
    testx.objects.add 'objects.csv'
    #testx.objects.add require './objects'
    #testx.functions.add require './functions'
    #testx.keywords.add require './keywords'
    beforeEach ->
      browser.ignoreSynchronization = true

