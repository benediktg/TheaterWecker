import React, { Component } from 'react'
import { View, StyleSheet, Text, Button, ActivityIndicator, AsyncStorage } from 'react-native'
import { Actions } from 'react-native-router-flux';
import Header from '../components/header'
import push from '../lib/push'
import api from '../lib/api'
import styles from '../styles'

// AsyncStorage: https://facebook.github.io/react-native/docs/asyncstorage.html
// ActivityIndicator: https://facebook.github.io/react-native/docs/activityindicator.html

export default class InitScene extends Component {
  constructor(props) {
    super(props);
    this.state = {
      progressText: 'Gleich gehts los..',
      skipButton: false,
      spinner: true
    }
  }

  async initPush() {
    // first init OneSignal
    this.setState({progressText: 'Initialisiere Push Dienst..'})
    console.log("init push")
    return await push.init(resolve, reject)
  }

  async registerDevice() {
    // console.log("registerDevice")
    this.setState({progressText: 'Registriere Gerät..'})
    return await api.registerDevice()
  }

  getCategories() {
    // console.log("getCategories")
    this.setState({progressText: 'Hole Kategorien..'})
    return api.getCategories()
  }

  getSubscriptions() {
    // console.log("getSubscriptions")
    this.setState({progressText: 'Hole Subscriptions..'})
    return api.getSubscriptions()
  }

  async saveCategories(categories) {
    console.log("AsyncStorage.setItem", categories)
    this.setState({progressText: 'Cache Kategorien..'})
    return await AsyncStorage.setItem('@TW:categories', JSON.stringify(categories))
  }
  async saveSubscriptions(subscriptions) {
    console.log("AsyncStorage.setItem", subscriptions)
    this.setState({progressText: 'Cache Subscriptions..'})
    return await AsyncStorage.setItem('@TW:subscriptions', JSON.stringify(subscriptions))
  }

  async componentDidMount() {
    try {
      let done = this.initPush()
      let verified = await this.registerDevice()
      // verified = true // TEST!!

      if (!verified) {
        // console.log("mustVerify")
        Actions.mustVerify()
        return
      } 

      let categories = this.getCategories()
      // let catStored = this.saveCategories(categories)

      // let subscriptions = this.getSubscriptions()
      // let subsStored = this.saveSubscriptions(subscriptions)
      
      // then switch to Main scene
      // console.log("Actions.main")
      this.setState({progressText: 'Lade Maske..'})
      Actions.main()
    
    // show errors
    } catch(error) {
      console.warn(error)
      this.setState({
        progressText: `Es ist ein Fehler aufgetreten: ${error}`,
        skipButton: true,
        spinner: false
      })
    }
  }

  render() {
    return (
        <View style={[styles.body, {flex: 1, flexDirection: 'column'}]}>
          <View style={{flex: 1}}>
            <Header/>
          </View>
          <View style={{flex: 5}}>
              <View style={styles.initContainer}>
                <Text style={{marginBottom: 20}}>{this.state.progressText}</Text>
                {this.state.skipButton ? <Button title="Überspringen" onPress={Actions.main} /> : null}
                {this.state.spinner ? <ActivityIndicator size="large" /> : null }
              </View>
          </View>
        </View>
    )
  }
}
