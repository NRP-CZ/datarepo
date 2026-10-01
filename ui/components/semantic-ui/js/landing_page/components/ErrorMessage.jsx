import React from "react";
import PropTypes from "prop-types";
import { Container, Grid, GridColumn, Message } from "semantic-ui-react";

function ErrorMessage({ message }) {
  return (
    <Container>
      <Grid padded>
        <GridColumn>
          <Message negative>
            <p>{message}</p>
          </Message>
        </GridColumn>
      </Grid>
    </Container>
  );
}

ErrorMessage.propTypes = {
  message: PropTypes.string,
};

export default ErrorMessage;