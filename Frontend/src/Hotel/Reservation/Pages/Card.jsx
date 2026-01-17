import React from 'react'
import Card from "../../../stories/Card"

const Card = () => {
    return (
        <div><Card
            variant="room"
            roomNo={202}
            available
            adult={2}
            child={3}
            selected={false}
            onClick={() => { }}
        />
        </div>
    )
}

export default Card