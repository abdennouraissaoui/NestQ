import React from "react"
import { Card, Tooltip } from "antd"
import ScrollMenu from 'react-horizontal-scrolling-menu';
// import "./Books.css"
const { Meta } = Card;
const booksRead = []
const Arrow = ({ text, className }) => {
    return (
        <div
            className={className}
        >{text}</div>
    );
};
const ArrowLeft = Arrow({ text: '<', className: 'arrow-prev' });
const ArrowRight = Arrow({ text: '>', className: 'arrow-next' });

const Books = () => {
    const booksData = booksRead.map((book, index) => {
        return (
            <a href={book.link} className="menu-item" key={index} style={{ padding: "10px" }}>
                <Tooltip title={book.name} >
                    <Card

                        hoverable
                        style={{ width: 200 }}
                        cover={<img alt={book.name} src={book.image} />}
                    >
                        <Meta title={book.name} description="www.goodreads.com" />
                    </Card>
                </Tooltip>
            </a>
        )
    })

    return (
        <ScrollMenu
            arrowLeft={ArrowLeft}
            arrowRight={ArrowRight}
            data={booksData}
            wheel={false}
        >

        </ScrollMenu>
    )
}

export default Books;