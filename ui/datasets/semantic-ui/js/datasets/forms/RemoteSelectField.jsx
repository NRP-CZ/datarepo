// This file is part of React-Invenio-Deposit
// Copyright (C) 2020 CERN.
// Copyright (C) 2020-2021 Northwestern University.
//
// React-Invenio-Deposit is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";
import _debounce from "lodash/debounce";
import _uniqBy from "lodash/uniqBy";
import _isEqual from "lodash/isEqual";
import PropTypes from "prop-types";
import queryString from "query-string";
import React, { Component } from "react";
import { Message } from "semantic-ui-react";
import { withCancel, SelectField } from "react-invenio-forms";
import uniqBy from "lodash/uniqBy";

const DEFAULT_SUGGESTION_SIZE = 20;

const serializeSuggestions = (suggestions) =>
  suggestions.map((item) => ({
    text: item.title,
    value: item.id,
    key: item.id,
  }));

export class RemoteSelectField extends Component {
  constructor(props) {
    super(props);
    const initialSuggestions = props.initialSuggestions
      ? props.serializeSuggestions(props.initialSuggestions)
      : [];
    this.state = {
      isFetching: false,
      suggestions: initialSuggestions,
      selectedSuggestions: initialSuggestions,
      error: false,
      searchQuery: null,
      open: false,
    };
  }

  componentWillUnmount() {
    this.cancellableAction && this.cancellableAction.cancel();
  }

  onSelectValue = (event, { options, value, ...otherData }, callbackFunc) => {
    const { multiple } = this.props;
    const newSelectedSuggestions = options.filter((item) => {
      if (multiple) {
        // "value" is an array so check if it includes the option's value
        return value.includes(item.value);
      } else {
        // "value" is a string so we just compare directly
        return item.value === value;
      }
    });

    this.setState(
      {
        selectedSuggestions: newSelectedSuggestions,
        searchQuery: null,
        error: false,
        open: !!multiple,
      },
      () => callbackFunc(newSelectedSuggestions)
    );
  };

  handleAddition = (e, { value }, callbackFunc) => {
    const { serializeAddedValue } = this.props;
    const { selectedSuggestions } = this.state;
    const selectedSuggestion = serializeAddedValue
      ? serializeAddedValue(value)
      : { text: value, value, key: value, name: value };

    const newSelectedSuggestions = [...selectedSuggestions, selectedSuggestion];

    this.setState(
      (prevState) => ({
        selectedSuggestions: newSelectedSuggestions,
        suggestions: _uniqBy(
          [...prevState.suggestions, ...newSelectedSuggestions],
          "value"
        ),
        searchQuery: null,
      }),
      () => callbackFunc(newSelectedSuggestions)
    );
  };

  onSearchChange = _debounce(async (e, { searchQuery }) => {
    this.cancellableAction && this.cancellableAction.cancel();
    await this.executeSearch(searchQuery);
    // eslint-disable-next-line react/destructuring-assignment
  }, this.props.debounceTime); // can't destructure as prop variable is used outside the inner function

  executeSearch = async (searchQuery) => {
    const { preSearchChange, serializeSuggestions } = this.props;
    const query = preSearchChange(searchQuery);
    // If there is no query change, then display prevState suggestions
    const { searchQuery: prevSearchQuery } = this.state;
    if (prevSearchQuery === searchQuery) {
      return;
    }
    this.setState({ isFetching: true, searchQuery: query });
    try {
      const suggestions = await this.fetchSuggestions(query);

      const serializedSuggestions = serializeSuggestions(suggestions);
      this.setState((prevState) => ({
        suggestions: _uniqBy(
          [...prevState.selectedSuggestions, ...serializedSuggestions],
          "key"
        ),
        isFetching: false,
        error: false,
        open: true,
      }));
    } catch (e) {
      console.error(e);
      this.setState({
        error: true,
        isFetching: false,
      });
    }
  };

  searchIfNoSuggestions = async (newSelectedSuggestions) => {
    // If all the suggestions from the search query are selected, fetch all suggestions via API
    const { suggestions } = this.state;
    if (_isEqual(newSelectedSuggestions, suggestions)) {
      await this.executeSearch("");
    }
  };

  fetchSuggestions = async (searchQuery) => {
    const {
      suggestionAPIUrl,
      suggestionAPIQueryParams,
      suggestionAPIHeaders,
      searchQueryParamName,
    } = this.props;

    this.cancellableAction = withCancel(
      axios.get(suggestionAPIUrl, {
        params: {
          [searchQueryParamName]: searchQuery,
          size: DEFAULT_SUGGESTION_SIZE,
          ...suggestionAPIQueryParams,
        },
        headers: suggestionAPIHeaders,
        // There is a bug in axios that prevents brackets from being encoded,
        // remove the paramsSerializer when fixed.
        // https://github.com/axios/axios/issues/3316
        paramsSerializer: (params) =>
          queryString.stringify(params, { arrayFormat: "repeat" }),
      })
    );

    try {
      const response = await this.cancellableAction.promise;
      return response?.data?.hits?.hits;
    } catch (e) {
      console.error(e);
    }
  };

  getNoResultsMessage = () => {
    const {
      loadingMessage,
      suggestionsErrorMessage,
      noQueryMessage,
      noResultsMessage,
    } = this.props;
    const { isFetching, error, searchQuery } = this.state;
    if (isFetching) {
      return loadingMessage;
    }
    if (error) {
      return <Message negative size="mini" content={suggestionsErrorMessage} />;
    }
    if (!searchQuery) {
      return noQueryMessage;
    }
    return noResultsMessage;
  };

  onClose = () => {
    this.setState({ open: false });
  };

  onBlur = () => {
    const { searchOnFocus } = this.props;
    this.setState((prevState) => ({
      open: false,
      error: false,
      searchQuery: searchOnFocus ? prevState.searchQuery : null,
      suggestions: searchOnFocus
        ? [
            ...this.props.serializeSuggestions(this.props.initialSuggestions),
            ...prevState.suggestions,
          ]
        : uniqBy(
            [
              ...this.props.serializeSuggestions(this.props.initialSuggestions),
              ...prevState.selectedSuggestions,
            ],
            "value"
          ),
    }));
  };

  onFocus = async () => {
    this.setState({ open: true });
    const { searchOnFocus } = this.props;
    if (searchOnFocus) {
      const { searchQuery } = this.state;
      await this.executeSearch(searchQuery || "");
    }
  };

  getProps = () => {
    const {
      fieldPath,
      suggestionAPIUrl,
      suggestionAPIQueryParams,
      serializeSuggestions,
      serializeAddedValue,
      suggestionAPIHeaders,
      debounceTime,
      searchQueryParamName,
      noResultsMessage,
      loadingMessage,
      suggestionsErrorMessage,
      noQueryMessage,
      initialSuggestions,
      preSearchChange,
      onValueChange,
      search,
      isFocused,
      ...uiProps
    } = this.props;
    const compProps = {
      fieldPath,
      suggestionAPIUrl,
      suggestionAPIQueryParams,
      suggestionAPIHeaders,
      serializeSuggestions,
      serializeAddedValue,
      debounceTime,
      searchQueryParamName,
      noResultsMessage,
      loadingMessage,
      suggestionsErrorMessage,
      noQueryMessage,
      initialSuggestions,
      preSearchChange,
      onValueChange,
      search,
      isFocused,
    };
    return { compProps, uiProps };
  };

  render() {
    const { compProps, uiProps } = this.getProps();
    const { error, suggestions, open, isFetching } = this.state;
    return (
      <SelectField
        allowAdditions={error ? false : uiProps.allowAdditions}
        fieldPath={compProps.fieldPath}
        options={suggestions}
        noResultsMessage={this.getNoResultsMessage()}
        search={compProps.search}
        searchInput={{
          id: compProps.fieldPath,
          autoFocus: compProps.isFocused,
        }}
        lazyLoad
        open={open}
        onClose={this.onClose}
        onFocus={this.onFocus}
        onBlur={this.onBlur}
        onSearchChange={this.onSearchChange}
        onAddItem={({ event, data, formikProps }) => {
          this.handleAddition(event, data, (selectedSuggestions) => {
            if (compProps.onValueChange) {
              compProps.onValueChange(
                { event, data, formikProps },
                selectedSuggestions
              );
            }
          });
        }}
        onChange={({ event, data, formikProps }) => {
          this.onSelectValue(event, data, (selectedSuggestions) => {
            if (compProps.onValueChange) {
              compProps.onValueChange(
                { event, data, formikProps },
                selectedSuggestions
              );
            } else {
              formikProps.form.setFieldValue(compProps.fieldPath, data.value);
            }
          });
        }}
        loading={isFetching}
        className="invenio-remote-select-field"
        {...uiProps}
      />
    );
  }
}

RemoteSelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  suggestionAPIUrl: PropTypes.string.isRequired,
  suggestionAPIQueryParams: PropTypes.object,
  suggestionAPIHeaders: PropTypes.object,
  serializeSuggestions: PropTypes.func,
  serializeAddedValue: PropTypes.func,
  initialSuggestions: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.object),
    PropTypes.object,
  ]),
  debounceTime: PropTypes.number,
  noResultsMessage: PropTypes.string,
  loadingMessage: PropTypes.string,
  suggestionsErrorMessage: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.object,
  ]),
  noQueryMessage: PropTypes.string,
  searchQueryParamName: PropTypes.string,
  preSearchChange: PropTypes.func, // Takes a string and returns a string
  onValueChange: PropTypes.func, // Takes the SUI hanf and updated selectedSuggestions
  search: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  multiple: PropTypes.bool,
  isFocused: PropTypes.bool,
  searchOnFocus: PropTypes.bool,
};

RemoteSelectField.defaultProps = {
  debounceTime: 500,
  suggestionAPIQueryParams: {},
  suggestionAPIHeaders: {},
  serializeSuggestions: serializeSuggestions,
  searchQueryParamName: "suggest",
  suggestionsErrorMessage: "Something went wrong...",
  noQueryMessage: "Search...",
  noResultsMessage: "No results found.",
  loadingMessage: "Loading...",
  preSearchChange: (x) => x,
  search: true,
  multiple: false,
  serializeAddedValue: undefined,
  initialSuggestions: [],
  onValueChange: undefined,
  isFocused: false,
  searchOnFocus: false,
};
